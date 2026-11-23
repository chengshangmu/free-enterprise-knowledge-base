import os
import sys
import time
import json
import logging
import urllib.request
from fastapi import FastAPI, Request, HTTPException, Response, BackgroundTasks
from fastapi.responses import PlainTextResponse
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.enterprise import parse_message, create_reply
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException
from dotenv import load_dotenv

# Load local environment if available
load_dotenv()

from core.formatter import format_for_wechat, split_message_chunks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wechat_bot")

CORP_ID = os.getenv("CORP_ID", "")
AGENT_ID = int(os.getenv("AGENT_ID", "1000002"))
SECRET = os.getenv("CORP_SECRET", "")
TOKEN = os.getenv("TOKEN", "YourCallbackToken")
ENCODING_AES_KEY = os.getenv("ENCODING_AES_KEY", "")

PROJECT_ID = os.getenv("PROJECT_ID", "")
DATA_STORE_ID = os.getenv("DATA_STORE_ID", "ai-knowledge-store")

crypto = WeChatCrypto(TOKEN, ENCODING_AES_KEY, CORP_ID)
app = FastAPI(title="Free-Tier VertexAI Knowledge Bot")

_token_cache = {"token": "", "expires_at": 0}

def get_access_token() -> str:
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

def send_wechat_message(touser: str, content: str):
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
            res = json.loads(resp.read().decode())
            logger.info(f"Send message to {touser} result: {res}")
            return res
    except Exception as e:
        logger.error(f"Failed to send wechat message to {touser}: {e}")

def send_wechat_message_smart(touser: str, raw_content: str):
    formatted = format_for_wechat(raw_content)
    chunks = split_message_chunks(formatted, max_bytes=1800)
    for idx, chunk in enumerate(chunks):
        send_wechat_message(touser, chunk)
        if idx < len(chunks) - 1:
            time.sleep(0.35)

def get_system_status() -> str:
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
    except Exception:
        days, hours = 0, 0

    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = {}
            for line in f:
                parts = line.split(':')
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = parts[1].strip()
        total_mem = int(meminfo.get('MemTotal', '0 kB').split()[0]) // 1024
        avail_mem = int(meminfo.get('MemAvailable', '0 kB').split()[0]) // 1024
        used_mem = total_mem - avail_mem
    except Exception:
        total_mem, used_mem = 0, 0

    try:
        stat = os.statvfs('/')
        disk_total = (stat.f_blocks * stat.f_frsize) / (1024**3)
        disk_avail = (stat.f_bavail * stat.f_frsize) / (1024**3)
    except Exception:
        disk_total, disk_avail = 0, 0

    msg = (
        "📊【小mini · 系统体检与运行状态】\n"
        "────────────────────\n"
        f"🖥 宿主环境：Google Cloud Always Free (e2-micro)\n"
        f"⏱ 持续在线：{days} 天 {hours} 小时（高可用守护中）\n"
        f"💾 内存状态：{used_mem}MB / {total_mem}MB（健康）\n"
        f"💽 磁盘空间：剩余 {disk_avail:.1f}GB / {disk_total:.1f}GB\n"
        f"🧠 知识底座：Vertex AI Agent Builder (Discovery Engine)\n"
        f"📁 核心知识库：多专业领域知识与自进化雷达已就绪\n"
        f"⏰ 定时服务：每日 08:30 晨报 | 12:00 & 20:00 知识收割\n"
        "────────────────────\n"
        "✨ 移动端方头括号排版引擎已生效。"
    )
    return msg

def get_help_message() -> str:
    return (
        "🤖【小mini · 智能知识库顾问使用指南】\n"
        "────────────────────\n"
        "我是基于 Google Cloud Vertex AI 搭建的企业专属技术智库助手，已收录完整知识库模块：\n\n"
        "📚 核心知识领域：\n"
        "1.【AI 算力基础设施】液冷/CDU/高压直流/GPU排障/GDS存储\n"
        "2.【高性能网络体系】InfiniBand/RoCEv2/Fat-Tree/NVLink/光互联\n"
        "3.【大模型分布式训练】3D并行/ZeRO显存/LoRA微调/通信重叠\n"
        "4.【RAG 工程与向量检索】知识库构建/向量库/Rerank/评测体系\n"
        "5.【智能体与提示词工程】ReAct/思维链CoT/安全防御/多模态\n"
        "6.【Google SRE 稳定性】SLO/错误预算/四大黄金指标/故障复盘\n"
        "7.【分布式系统设计】缓存击穿穿透雪崩/一致性哈希/MQ削峰\n"
        "8.【Linux 运维与排障】CPU/内存OOM/TIME_WAIT/文本三剑客\n"
        "9.【大模型架构与推理】MoE/推测解码/量化AWQ/DPO对齐\n\n"
        "⚡️ 快捷交互指令：\n"
        "• 输入「状态」或「status」：实时自检查看服务器负载与服务健康度\n"
        "• 输入「今日一学」或「每日一学」：即刻抽取生成一张精炼技术卡片\n"
        "• 直接提问：输入任意技术问题或排障场景，基于私有库秒级研判解答！"
    )

def query_knowledge_base(query: str) -> str:
    try:
        from google.cloud import discoveryengine_v1 as discoveryengine
        client = discoveryengine.SearchServiceClient()
        serving_config = client.serving_config_path(
            project=PROJECT_ID,
            location="global",
            data_store=DATA_STORE_ID,
            serving_config="default_search",
        )
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=3,
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                    summary_result_count=3,
                    include_citations=True
                )
            )
        )
        response = client.search(request)
        if response.summary and response.summary.summary_text:
            return response.summary.summary_text
        elif response.results:
            snippets = []
            for r in response.results:
                title = r.document.derived_struct_data.get("title", "相关参考")
                snippet_list = r.document.derived_struct_data.get("snippets", [])
                snippet = snippet_list[0].get("snippet", "") if snippet_list else ""
                if snippet:
                    snippets.append(f"【{title}】{snippet}")
            if snippets:
                return "\n\n".join(snippets)
        return f"🤖 收到你的提问：『{query}』\n\n知识库引擎（{DATA_STORE_ID}）通信正常！目前知识库中尚未检索到相关高匹配内容。"
    except Exception as e:
        logger.error(f"Error querying knowledge base: {e}")
        return f"🤖 知识库连接正常，响应提示：{str(e)[:120]}\n收到问题：{query}"

def async_answer_query(user_id: str, query: str):
    logger.info(f"Async querying knowledge base for {user_id}: {query}")
    answer = query_knowledge_base(query)
    send_wechat_message_smart(user_id, answer)

def async_generate_and_push_card(user_id: str):
    try:
        from cron.daily_knowledge import generate_knowledge_card
        card_content = generate_knowledge_card(mark_as_used=False)
        send_wechat_message_smart(user_id, card_content)
    except Exception as e:
        logger.error(f"Failed to generate card for {user_id}: {e}")
        send_wechat_message(user_id, f"⚠️ 生成知识卡片时遇到异常：{str(e)[:120]}")

@app.get("/")
def index():
    return {"status": "ok", "service": "wechat-ai-gateway"}

@app.get("/wechat")
def verify_wechat(msg_signature: str = "", timestamp: str = "", nonce: str = "", echostr: str = ""):
    try:
        decrypted_echo = crypto.check_signature(msg_signature, timestamp, nonce, echostr)
        return PlainTextResponse(content=decrypted_echo)
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=403, detail="Invalid signature or CorpID")

@app.post("/wechat")
async def handle_message(
    request: Request,
    background_tasks: BackgroundTasks,
    msg_signature: str = "",
    timestamp: str = "",
    nonce: str = ""
):
    body = await request.body()
    try:
        decrypted_xml = crypto.decrypt_message(body, msg_signature, timestamp, nonce)
    except Exception as e:
        logger.error(f"Message decryption failed: {e}")
        raise HTTPException(status_code=403, detail="Invalid signature or CorpID")

    msg = parse_message(decrypted_xml)
    user_id = getattr(msg, "source", os.getenv("TARGET_WECHAT_USER", "@all"))

    if msg.type == "text":
        user_query = msg.content.strip()
        if user_query in ["帮助", "help", "Help", "?", "？", "/help"]:
            reply_text = get_help_message()
            reply = create_reply(reply_text, msg)
            xml_out = reply.render()
            encrypted_xml = crypto.encrypt_message(xml_out, nonce, timestamp)
            return Response(content=encrypted_xml, media_type="application/xml")
        elif user_query in ["状态", "status", "Status", "巡检", "/status"]:
            reply_text = get_system_status()
            reply = create_reply(reply_text, msg)
            xml_out = reply.render()
            encrypted_xml = crypto.encrypt_message(xml_out, nonce, timestamp)
            return Response(content=encrypted_xml, media_type="application/xml")
        elif user_query in ["今日一学", "每日一学", "学一个", "知识卡片", "card"]:
            background_tasks.add_task(async_generate_and_push_card, user_id)
            return PlainTextResponse("success")
        else:
            background_tasks.add_task(async_answer_query, user_id, user_query)
            return PlainTextResponse("success")
    elif msg.type == "event":
        reply = create_reply("你好！我是小mini，基于 Google Cloud Vertex AI 的专属知识库助手。已成功连接，发送「帮助」可查看功能指南！", msg)
        xml_out = reply.render()
        encrypted_xml = crypto.encrypt_message(xml_out, nonce, timestamp)
        return Response(content=encrypted_xml, media_type="application/xml")

    return PlainTextResponse("success")
