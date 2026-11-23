# Free-Enterprise-Knowledge-Base (云原生自进化企业微信技术智库)

<p align="center">
  <a href="README.md"><b>简体中文</b></a> | <a href="README_en.md"><b>English</b></a>
</p>

> 🚀 **基于 Google Cloud 永久免费层（Always Free）与 Vertex AI 构建的轻量级、自进化企业微信技术智库助手。**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Google Cloud](https://img.shields.io/badge/GCP-Always_Free-yellow.svg)](https://cloud.google.com/free)
[![WeChat Work](https://img.shields.io/badge/Enterprise_WeChat-Compatible-brightgreen.svg)](https://work.weixin.qq.com/)

---

## 🌟 核心特性与架构亮点

1. 💰 **永久免费云端底座 (Zero Server Cost)**
   - 全链路适配 Google Cloud Always Free（`e2-micro`，1GB 内存，30GB 硬盘，静态公网 IP）；
   - 常驻物理内存仅占用 **~50MB**，无需重型中间件（无 Docker/无 MySQL/无 Redis 负担）。

2. 🧠 **自进化闭环架构 (Self-Evolving Knowledge Loop)**
   - 监听全球顶流技术源（ArXiv、Google Research、Hugging Face、AWS、Netflix、Uber 等）；
   - 大模型（Gemini）担当“AI 质检主编”，以 **8.0 分为入库红线**，自动过滤公关营销水文；
   - 自动重构为四段式 Markdown 标准文档，存入云存储桶并自动触发 Google Discovery Engine 增量向量化；
   - 知识库每日自动生长进化，微信即时同步推送速读研报。

3. 📱 **移动端方头括号 【 】 卡片排版体系**
   - 自动滤除大模型角标源码（如 `[1]`、`[2]`）；
   - 自动将 LaTeX 数学公式转译为微信原生 Unicode 符号；
   - 采用商务高级感「方头括号 【 】」分层，彻底告别安卓与电脑端双星号 `**` 乱码；
   - 超长回复智能切片分段推送，**彻底根除微信 2048 字节截断 Bug**。

4. ⚡️ **企业微信防超时高并发网关**
   - 针对大模型多秒检索耗时，采用 **20ms 快速 Ack 响应**，后台 `BackgroundTasks` 异步精准推送，100% 杜绝微信 5 秒超时导致的重复重试。

---

## 🏗 系统架构图

```
                       ┌──────────────────────────────┐
                       │ 全球前沿技术源 (RSS / ArXiv) │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                        【自进化收割引擎 Harvester】
                         (Trafilatura + Feedparser)
                                      │
                                      ▼
                        【Gemini 智审主编 (≥8.0分)】
                        (四段式结构化提炼 + 7大分类映射)
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
   【企业微信速递研报 (WeChat)】           【云端存储桶 (Cloud Storage)】
   (推送至用户企业微信聊天窗口)                           │
                                                           ▼
                                            【Vertex AI Discovery Engine】
                                            (免运维全托管切片与向量化检索)
                                                           │
                                                           ▼
    【企业微信用户交互】 ◄────── 异步推送 ────── 【小mini 问答大脑】
```

---

## 🚀 5 分钟快速上手

### 1. 克隆项目与安装依赖
```bash
git clone https://github.com/chengshangmu/free-enterprise-knowledge-base.git
cd free-enterprise-knowledge-base

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量
复制环境变量模板并填入您的真实凭证：
```bash
cp .env.example .env
vim .env
```

### 3. 一键初始化与运行
```bash
# 1. 优化虚拟机（配置 4GB Swap、BBR、时区）
bash scripts/setup_vm.sh

# 2. 注册系统服务开机自启
bash scripts/setup_systemd.sh

# 3. 配置定时任务（晨报与知识收割）
bash scripts/setup_cron.sh
```

---

## 📋 快捷交互指令

在企业微信中对机器人发送：
* 💬 `状态` / `status`：查看云主机负载、内存利用率及知识底座健康指标
* 💬 `帮助` / `help`：获取 9 大技术知识领域总览与使用技巧
* 💬 `今日一学` / `每日一学`：现场抽取并生成一张精炼技术卡片
* 💬 **任意问题**：直接输入技术疑惑，基于专属私有库秒级研判解答

---

## ⚠️ 免责声明与 Google Cloud 免费层避坑指南

> **免责声明**：  
> 本项目仅供技术研究与交流使用。使用者需严格遵守 Google Cloud、腾讯企业微信等平台的服务条款。所有使用者在部署过程中应自行管理其云平台账单与配额，项目作者不对任何因使用者配置不当可能产生的扣费承担责任。

### 免费层关键配置红线：
1. **区域限制**：计算实例必须开在 `us-central1`、`us-west1` 或 `us-east1`；
2. **机型与磁盘**：必须选择 `e2-micro`（共享 2 核 / 1GB 内存），磁盘选择 **标准永久性磁盘（pd-standard）** 且大小 $\le 30\text{GB}$（切勿误选 SSD 或平衡磁盘）；
3. **单实例额度**：每个结算账号仅限 1 台免费实例；
4. **出站流量**：免费层每月包含 1GB 互联网出站流量，本项目轻量设计已严格控流，请勿用于大文件下载或视频分发。

---

## 📄 License
本项目基于 [Apache License 2.0](LICENSE) 协议开源。
