import urllib.request
import json
import datetime
import random
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.bot_gateway import query_knowledge_base, send_wechat_message_smart

CORP_ID = os.getenv("CORP_ID", "")
SECRET = os.getenv("CORP_SECRET", "")
AGENT_ID = int(os.getenv("AGENT_ID", "1000002"))
TARGET_USER = os.getenv("TARGET_WECHAT_USER", "@all")
HISTORY_FILE = "push_history.json"

KNOWLEDGE_TOPICS = [
    # 1. AI 算力与基础设施
    {"topic": "AI 算力集群冷板式液冷与浸没式液冷架构设计", "category": "AI 算力基础设施"},
    {"topic": "CDU（冷量分配单元）与二次侧流体管网运行机制", "category": "AI 算力基础设施"},
    {"topic": "AI 集群供电母线槽（Busbar）与高压直流（HVDC）设计", "category": "AI 算力基础设施"},
    {"topic": "GPU Direct Storage (GDS) 与 NVMe-oF 并行存储架构", "category": "AI 存储体系"},
    {"topic": "大模型分布式训练 3D 并行（DP、TP、PP、EP）核心原理", "category": "分布式训练"},
    {"topic": "ZeRO 显存优化技术（ZeRO-1/2/3）与 FSDP 全切片数据并行", "category": "分布式训练"},
    {"topic": "大模型计算通信重叠（Overlap）与流水线气泡（Bubble）消除", "category": "训练性能优化"},
    {"topic": "AI 集群 GPU 硬件故障与 Xid 典型报错排查流程", "category": "集群运维排障"},
    {"topic": "AI 训练慢节点（Straggler）检测与静默数据损坏（SDC）诊断", "category": "集群高可用"},
    
    # 2. 数据中心与高性能网络体系
    {"topic": "InfiniBand 架构核心原理与逐跳信用流控机制", "category": "高性能网络"},
    {"topic": "RoCEv2 与 InfiniBand 无损以太网架构深度对比与选型", "category": "高性能网络"},
    {"topic": "AI 万卡集群 Fat-Tree 拓扑与 Spine-Leaf 架构设计", "category": "网络拓扑"},
    {"topic": "Rail-Optimized（轨道优化）AI 集群网络拓扑规划", "category": "集群网络规划"},
    {"topic": "NVLink 与 NVSwitch 芯片级高速互联 Scale-Up 架构", "category": "芯片互联架构"},
    {"topic": "NCCL 集合通信算法与网络物理拓扑映射机制", "category": "集合通信优化"},
    {"topic": "Google Jupiter 数据中心光电混合网络演进历程", "category": "前沿网络技术"},
    {"topic": "Google OCS（光路交换机）与 AI Hypercomputer 超级计算机互联", "category": "光互联技术"},
    
    # 3. 大模型应用与 RAG 工程
    {"topic": "RAG 检索增强生成高级架构与全流程设计", "category": "RAG 工程落地"},
    {"topic": "向量数据库检索优化与 Rerank 语义重排算法", "category": "检索算法与向量库"},
    {"topic": "提示词工程系统化指南：Few-Shot 与思维链（CoT）", "category": "提示词工程"},
    {"topic": "AI Agent 智能体核心架构、ReAct 范式与工具调用（Tool Use）", "category": "智能体架构"},
    {"topic": "大模型轻量化微调技术：LoRA 与 QLoRA 底层原理", "category": "模型微调与量化"},
    {"topic": "RAG 检索评估框架：RAGAS 指标体系与召回率评测", "category": "AI 评测与质检"},
    
    # 4. Google SRE 生产可用性
    {"topic": "Google SRE 核心哲学：SLI、SLO 与错误预算（Error Budget）", "category": "高可用架构"},
    {"topic": "系统过载保护（Load Shedding）与级联故障熔断设计", "category": "高可用架构"},
    {"topic": "监控四大黄金指标（延迟、流量、错误、饱和度）", "category": "可观测性与监控"},
    {"topic": "无指责复盘（Blameless Postmortem）与故障应急流程", "category": "生产运维规范"},
    {"topic": "金丝雀发布（Canary Deployment）与平滑滚动升级实践", "category": "发布工程"},

    # 5. 分布式系统设计与高并发架构
    {"topic": "分布式系统高可用与高一致性模式权衡（CAP 定理与 BASE 理论）", "category": "系统设计与架构"},
    {"topic": "分布式缓存三大杀手：穿透、击穿、雪崩原理与全套防御方案", "category": "缓存与高并发"},
    {"topic": "一致性哈希（Consistent Hashing）算法在分布式存储与负载均衡中的应用", "category": "分布式核心算法"},
    {"topic": "负载均衡算法选型（轮询/权重/最少连接/IP Hash）与四层 vs 七层对比", "category": "高并发接入层"},
    {"topic": "消息队列（Message Queue）异步解耦与削峰填谷最佳实践", "category": "异步消息架构"},
    {"topic": "数据库分库分表与读写分离架构设计实践", "category": "数据持久层架构"},
    {"topic": "分布式锁实现原理深度对比：Redis Redlock vs ZooKeeper", "category": "分布式协调机制"},

    # 6. Linux 运维、内核与高频排障实战
    {"topic": "Linux CPU 100% 飙高定位方法与 top/perf 深度排查实战", "category": "Linux 性能排障"},
    {"topic": "Linux 内存 OOM Killer 机制与内存泄漏排查（/proc/meminfo 与 smem）", "category": "Linux 性能排障"},
    {"topic": "Linux 网络连接数暴涨与 TCP TIME_WAIT 深度调优", "category": "网络性能调优"},
    {"topic": "Linux 磁盘 I/O 瓶颈定位与 iostat/pidstat 性能分析", "category": "存储与I/O调优"},
    {"topic": "文本三剑客（grep、sed、awk）在海量日志分析中的高级实战技巧", "category": "自动化运维与日志"},

    # 7. 提示词工程高阶与安全防护
    {"topic": "思维树（Tree of Thoughts, ToT）与思维图（GoT）复杂推理范式", "category": "提示词工程高阶"},
    {"topic": "反思机制（Reflexion）与自我修正智能体设计", "category": "智能体高级范式"},
    {"topic": "大模型提示词注入攻击（Prompt Injection）与防越狱防御方案", "category": "大模型安全合规"},
    {"topic": "自动化提示词优化（APE & DSP）与结构化输出约束", "category": "提示词工程工具链"},

    # 8. 大模型前沿与推理优化
    {"topic": "推测解码（Speculative Decoding）大模型无损加速推理技术", "category": "大模型推理加速"},
    {"topic": "混合专家架构（Mixture of Experts, MoE）路由与稀疏激活原理", "category": "大模型架构前沿"},
    {"topic": "大模型权重量化技术：AWQ、GPTQ 与 GGUF 原理对比", "category": "模型量化与部署"},
    {"topic": "长上下文机制：RoPE 旋转位置编码与插值扩展方法", "category": "模型核心算法"},
    {"topic": "大模型对齐技术：RLHF、DPO 与 KTO 原理深度剖析", "category": "大模型对齐与偏好"}
]

def select_next_topic(mark_as_used=True):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            history = []
            
    available = [t for t in KNOWLEDGE_TOPICS if t["topic"] not in history]
    if not available:
        available = KNOWLEDGE_TOPICS
        history = []
        
    chosen = random.choice(available)
    if mark_as_used:
        history.append(chosen["topic"])
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: failed to save history: {e}")
        
    return chosen

def generate_knowledge_card(topic_info=None, mark_as_used=True):
    if not topic_info:
        topic_info = select_next_topic(mark_as_used=mark_as_used)
        
    topic = topic_info["topic"]
    category = topic_info["category"]
    
    prompt = (
        f"请根据知识库内容，针对【{topic}】这个核心主题，生成一份条理极其清晰、干货满满的【每日一学·知识精炼卡片】。"
        "要求："
        "1. 先用一句话给出核心定义/背景（讲透它是什么、解决什么痛点）；"
        "2. 提炼出 2~3 个最关键的技术要点或运作原理（有理有据，深入浅出）；"
        "3. 给出 1 条关键的工程实践选型经验或避坑忠告；"
        "语言严谨专业，适合工程人员晨间阅读。"
    )
    
    body_text = query_knowledge_base(prompt)
    
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    now = datetime.datetime.now()
    date_str = now.strftime("%Y年%m月%d日") + " " + weekdays[now.weekday()]
    
    header = f"📖【每日一学·知识库精选卡片】\n📅 {date_str} | 🏷 领域：{category}\n🎯 今日主题：『{topic}』\n"
    divider = "\n────────────────────\n"
    footer = "\n💡 提示：微信直接回复感兴趣的技术词，机器人将基于知识库为你深入解答。"
    
    return header + divider + body_text.strip() + divider + footer

if __name__ == "__main__":
    topic_info = select_next_topic(mark_as_used=True)
    card_content = generate_knowledge_card(topic_info)
    send_wechat_message_smart(TARGET_USER, card_content)
    print("Daily knowledge card executed successfully.")
