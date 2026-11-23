# Free-Enterprise-Knowledge-Base

<p align="center">
  <a href="README.md"><b>简体中文</b></a> | <a href="README_en.md"><b>English</b></a>
</p>

> 🚀 **An ultra-lightweight, self-evolving technical knowledge base and Enterprise WeChat AI assistant powered by Google Cloud Always Free tier and Vertex AI.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Google Cloud](https://img.shields.io/badge/GCP-Always_Free-yellow.svg)](https://cloud.google.com/free)
[![WeChat Work](https://img.shields.io/badge/Enterprise_WeChat-Compatible-brightgreen.svg)](https://work.weixin.qq.com/)

---

## 🌟 Key Features & Architectural Highlights

1. 💰 **Always-Free Cloud Infrastructure (Zero Server Cost)**
   - Tailored specifically for Google Cloud Always Free tier (`e2-micro`, 1GB RAM, 30GB disk, static public IPv4);
   - Idle memory footprint is only **~50MB** with zero heavyweight middleware bloat (No Docker, No MySQL, No Redis required).

2. 🧠 **Self-Evolving Knowledge Loop**
   - Continuously monitors premier global tech sources (ArXiv, Google Research, Hugging Face, AWS, Netflix, Uber Engineering, etc.);
   - Leverages Gemini as an "AI Chief Editor" with a strict **8.0/10 quality threshold** to filter out marketing fluff;
   - Automatically restructures articles into standardized 4-section Markdown documents, uploads them to Google Cloud Storage, and triggers Vertex AI Discovery Engine incremental vectorization;
   - The knowledge base evolves daily while pushing concise research briefings directly to WeChat.

3. 📱 **Mobile Card Typography Engine**
   - Automatically strips raw citation artifacts (e.g., `[1]`, `[2]`);
   - Converts LaTeX formulas into native Unicode mathematical symbols;
   - Employs a clean card hierarchy with Chinese square brackets `【 】`, eliminating unrendered double asterisks (`**`) across mobile and desktop WeChat clients;
   - Automatically chunks long replies exceeding 1800 bytes, **completely preventing WeChat's 2048-byte mid-sentence truncation bug**.

4. ⚡️ **Anti-Timeout Asynchronous Gateway**
   - Responds to WeChat's webhook callback within **20ms** to avoid the strict 5-second timeout and duplicate message retries;
   - Background tasks query Vertex AI Search and asynchronously push answers via Enterprise WeChat APIs.

---

## 🏗 Architecture Diagram

```
                       ┌─────────────────────────────────────────┐
                       │ Global Tech Sources (RSS / ArXiv feeds) │
                       └────────────────────┬────────────────────┘
                                            │
                                            ▼
                           【Headless Harvester Engine】
                             (Trafilatura + Feedparser)
                                            │
                                            ▼
                          【Gemini Quality Gating (≥8.0)】
                        (4-Section Structuring + Taxonomy)
                                            │
                 ┌──────────────────────────┴──────────────────────────┐
                 ▼                                                     ▼
   【WeChat Research Briefing】                            【Cloud Storage (GCS)】
   (Delivered to WeChat chat window)                                   │
                                                                       ▼
                                                        【Vertex AI Discovery Engine】
                                                        (Managed Chunking & Indexing)
                                                                       │
                                                                       ▼
    【Enterprise WeChat User】 ◄────── Async Push ────── 【AI Knowledge Assistant】
```

---

## 🚀 5-Minute Quickstart

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/chengshangmu/free-enterprise-knowledge-base.git
cd free-enterprise-knowledge-base

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the template and fill in your credentials:
```bash
cp .env.example .env
vim .env
```

### 3. Initialize & Deploy
```bash
# 1. Optimize VM (4GB Swap, BBR congestion control, Timezone)
bash scripts/setup_vm.sh

# 2. Register and start systemd daemon
bash scripts/setup_systemd.sh

# 3. Setup scheduled cron jobs (Morning card & Knowledge harvester)
bash scripts/setup_cron.sh
```

---

## 📋 Interactive Commands

Send the following commands to your bot in Enterprise WeChat:
* 💬 `status` / `状态`: View VM uptime, memory usage, and knowledge base vital signs
* 💬 `help` / `帮助`: View overview of core knowledge domains and usage tips
* 💬 `card` / `今日一学`: Instantly generate and push a curated daily knowledge card
* 💬 **Any Question**: Ask technical questions directly for instant, citation-grounded answers

---

## ⚠️ Disclaimer & GCP Free Tier Best Practices

> **Disclaimer**:  
> This project is for technical research and educational purposes only. Users must comply with the Terms of Service of Google Cloud and WeChat. Users are solely responsible for managing their cloud quotas and billing. The project author is not responsible for any unexpected cloud charges resulting from improper user configuration.

### GCP Always Free Tier Guidelines:
1. **Region Selection**: The instance must be created in `us-central1`, `us-west1`, or `us-east1`;
2. **Machine & Disk**: Choose `e2-micro` (2 vCPUs, 1GB RAM) and **Standard Persistent Disk (pd-standard)** with capacity $\le 30\text{GB}$ (do not select SSD or Balanced persistent disk);
3. **Instance Limit**: Exactly 1 free `e2-micro` instance per billing account;
4. **Egress Bandwidth**: Free tier includes 1GB/month external internet egress. This project is optimized for minimal network consumption, but avoid large file streaming or proxying.

---

## 📄 License
This project is open-sourced under the [Apache License 2.0](LICENSE).
