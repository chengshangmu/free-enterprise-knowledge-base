import os
import sys
import json
import time
import re
import datetime
import urllib.request
import feedparser
import trafilatura
from google.cloud import storage
from google.cloud import discoveryengine_v1 as discoveryengine
from dotenv import load_dotenv

load_dotenv()

CORP_ID = os.getenv("CORP_ID", "")
AGENT_ID = int(os.getenv("AGENT_ID", "1000002"))
SECRET = os.getenv("CORP_SECRET", "")
PROJECT_ID = os.getenv("PROJECT_ID", "")
DATA_STORE_ID = os.getenv("DATA_STORE_ID", "ai-knowledge-store")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TARGET_USER = os.getenv("TARGET_WECHAT_USER", "@all")
HISTORY_FILE = "harvest_history.json"

# Load config
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        TAXONOMY_CATEGORIES = config_data.get("taxonomy_categories", {})
        RSS_FEEDS = config_data.get("rss_feeds", [])
except Exception:
    TAXONOMY_CATEGORIES = {"ai-infra-systems": "AI 算力与基础设施"}
    RSS_FEEDS = []

_token_cache = {"token": "", "expires_at": 0}

def get_access_token():
    global _token_cache
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={SECRET}"
    req = urllib.request.urlopen(url, timeout=10)
    data = json.loads(req.read().decode())
    if data.get("errcode") != 0:
        raise Exception(f"Get token error: {data}")
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 7200) - 200
    return _token_cache["token"]

def send_wechat_push(content, touser=None):
    if not touser:
        touser = TARGET_USER
    try:
        token = get_access_token()
        send_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
        payload = {
            "touser": touser,
            "msgtype": "text",
            "agentid": AGENT_ID,
            "text": {"content": content},
            "safe": 0
        }
        req = urllib.request.Request(
            send_url,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error sending wechat push: {e}")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save history: {e}")

def call_gemini(prompt: str, max_tokens: int = 4096) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json"
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        res = json.loads(resp.read().decode())
        return res["candidates"][0]["content"]["parts"][0]["text"]

def evaluate_and_structure_article(title: str, text: str, url: str, source_name: str):
    prompt = f"""你是一名资深首席架构师和 AI 知识库技术主编。请对以下技术文献进行价值评估与分类清洗。

【可用分类目录清单】：
{json.dumps(TAXONOMY_CATEGORIES, ensure_ascii=False, indent=2)}

【技术文章信息】：
来源：{source_name}
原标题：{title}
原文链接：{url}
正文内容摘录（前 4000 字符）：
{text[:4000]}

【任务要求】：
1. 评估技术价值分数 quality_score（1.0 ~ 10.0）：8.0 以上为硬核架构/论文实战，低于 8.0 为浅显科普/营销新闻。
2. 判定归属分类 category：必须精确从清单中挑选。
3. 提取 3~5 个关键词 tags。
4. 撰写一份微信推送速读版 summary_wechat（约 200~300 字）。
5. 若 quality_score >= 8.0，生成结构化 Markdown 正文（包含标准 YAML Frontmatter 与四段式正文）。

请输出严格 JSON 格式：
{{
  "quality_score": 8.5,
  "category": "ai-infra-systems",
  "category_cn": "AI 算力与基础设施",
  "tags": ["NVLink", "GPU拓扑"],
  "is_ingest_worthy": true,
  "summary_wechat": "速读内容...",
  "structured_markdown": "规范Markdown文本..."
}}
"""
    raw_res = call_gemini(prompt)
    return json.loads(raw_res.strip())

def upload_to_gcs(local_path: str, gcs_blob_name: str):
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_blob_name)
    blob.upload_from_filename(local_path, content_type="text/markdown")
    return f"gs://{GCS_BUCKET_NAME}/{gcs_blob_name}"

def trigger_vertex_ai_import(gcs_uri: str):
    try:
        client = discoveryengine.DocumentServiceClient()
        parent = client.branch_path(
            project=PROJECT_ID,
            location="global",
            data_store=DATA_STORE_ID,
            branch="0",
        )
        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            gcs_source=discoveryengine.GcsSource(
                input_uris=[gcs_uri],
                data_schema="content"
            ),
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
        )
        operation = client.import_documents(request=request)
        return operation.operation.name
    except Exception as e:
        print(f"Error triggering Vertex AI import: {e}")
        return None

def harvest_and_process():
    history = load_history()
    processed_count = 0
    now_str = datetime.datetime.now().strftime("%Y-%m-%d")

    print(f"[{datetime.datetime.now()}] Starting Knowledge Harvesting...")
    
    for feed_info in RSS_FEEDS:
        feed_name = feed_info["name"]
        feed_url = feed_info["url"]
        
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            continue

        for entry in feed.entries[:5]:
            url = getattr(entry, "link", "")
            title = getattr(entry, "title", "Untitled")
            
            if not url or url in history:
                continue
                
            try:
                downloaded = trafilatura.fetch_url(url)
                if not downloaded:
                    history.append(url)
                    continue
                extracted_text = trafilatura.extract(downloaded)
                if not extracted_text or len(extracted_text) < 300:
                    history.append(url)
                    continue
            except Exception:
                history.append(url)
                continue

            try:
                eval_res = evaluate_and_structure_article(title, extracted_text, url, feed_name)
            except Exception:
                history.append(url)
                continue

            score = eval_res.get("quality_score", 0.0)
            category = eval_res.get("category", "ai-infra-systems")
            category_cn = TAXONOMY_CATEGORIES.get(category, category)
            is_worthy = eval_res.get("is_ingest_worthy", False) and score >= 8.0
            summary = eval_res.get("summary_wechat", "")

            if is_worthy:
                slug = re.sub(r'[^a-zA-Z0-9_\-\u4e00-\u9fa5]', '_', title)[:40].strip('_')
                filename = f"{now_str}_{slug}.md"
                gcs_path = f"auto-harvested/{category}/{filename}"
                local_temp = f"/tmp/{filename}"

                with open(local_temp, 'w', encoding='utf-8') as f:
                    f.write(eval_res.get("structured_markdown", ""))

                gcs_uri = upload_to_gcs(local_temp, gcs_path)
                try:
                    os.remove(local_temp)
                except Exception:
                    pass

                trigger_vertex_ai_import(gcs_uri)

                wechat_msg = (
                    f"🛰【自进化智库 · 前沿技术深度入库】\n"
                    f"📅 {now_str} | 🏷 领域：{category_cn}\n"
                    f"📌 主题：{title}\n"
                    f"📊 质量评分：{score}/10（高干货）\n"
                    f"────────────────────\n"
                    f"{summary}\n"
                    f"────────────────────\n"
                    f"✅ 状态：已标准化沉淀至 Google 知识库！\n"
                    f"💡 提示：您现在可直接向「小mini」提问该技术！"
                )
                send_wechat_push(wechat_msg)
                processed_count += 1

            history.append(url)
            save_history(history)

            if processed_count >= 1:
                return

if __name__ == "__main__":
    harvest_and_process()
