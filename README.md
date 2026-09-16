# MPSCB — 智能客服系统（英文服装电商）

基于 **Nanobot** 框架的智能客服机器人，面向**英文服装电商**：经飞书/钉钉回答 FAQ、用 RAG 检索真实商品评论、创建/查询工单、记录偏好、收集满意度，并带运维观测与反馈闭环。

## 能力全景

**核心客服（PRD 七项）**：FAQ 查询（语义检索）· 工单创建/查询 · 用户偏好 · 问题记录 · 转人工 · 满意度（1–5 星）

**智能化亮点**
- **RAG 语义匹配**：FAQ 用 embedding 向量相似度，「换个说法」也能命中（关键词匹配做不到）。
- **评论 RAG**：2.3 万条真实评论向量化，FAQ 未命中时召回相关评论 + LLM 生成回答。
- **运维观测**：命中率 / 满意度 / 工单统计报表，让智能效果可量化。
- **反馈闭环**：分析高频未命中问题 → 建议补 FAQ，知识库自我更新。

## 技术栈

| 层 | 选型 |
|----|------|
| Agent 框架 | Nanobot（`../nanobot`，本地源码） |
| 语言 | Python 3.11 |
| 数据存储 | SQLite（业务）+ 文件偏好 |
| AI 模型 | DeepSeek（chat） |
| RAG embedding | sentence-transformers（`all-MiniLM-L6-v2`） |
| 接入平台 | 飞书 + 钉钉（长连接） |
| 部署 | Docker / Docker Compose |

## 目录结构

```
MPSCB/
├── CLAUDE.md            # AI 协作开发规范
├── agent/               # nanobot agent（workspace）
│   ├── SOUL.md          # 人设（英文客服）
│   ├── AGENTS.md        # 行为规范
│   └── memory/          # 长期记忆
├── config.json          # nanobot 配置（DeepSeek + 飞书 + 钉钉 + MCP）
├── src/mpscb/
│   ├── domain/          # 模型 + 服务 + RAG（rag.py / review_rag.py / stats.py）
│   ├── tools/           # 6 个 nanobot 工具（含 search_reviews）
│   └── mcp_server/      # 工单 MCP Server
├── scripts/             # faq_cli / ticket_cli / stats_cli / suggest_faq / run_bot
├── tests/               # pytest（53 个）
└── PRD.md / 技术文档.md / 项目流程.md / TESTING.md / CHALLENGES.md
```

## 快速开始

```bash
# 1. 环境
conda create -n mpscb python=3.11 -y && conda activate mpscb

# 2. 安装 nanobot（本地源码）+ 本项目
pip install -e ../nanobot
pip install -e .          # 含 [rag] extra：pip install -e .[rag]

# 3. 配置 .env（密钥）
#    DEEPSEEK_API_KEY / FEISHU_APP_ID / FEISHU_APP_SECRET / DINGTALK_CLIENT_ID / DINGTALK_CLIENT_SECRET

# 4. 建评论索引（RAG，约 1 分钟）
python scripts/build_review_index.py

# 5. 导入 FAQ + 运行
python scripts/faq_cli.py reset --file scripts/faq_seed_en.json
python scripts/run_bot.py
```

## 常用命令

```bash
python scripts/faq_cli.py list               # 查看 FAQ
python scripts/ticket_cli.py stats           # 工单统计
python scripts/ticket_cli.py list --status waiting_human
python scripts/stats_cli.py                  # 运营报表（命中率/满意度/工单）
python scripts/suggest_faq.py                # 反馈闭环：高频未命中建议
python scripts/build_review_index.py         # 构建评论向量索引（RAG）
```

## Docker 部署

```bash
cd ~/CODE/NanobotProject/MPSCB
docker compose up -d --build   # 构建并后台启动
docker compose logs -f         # 看日志
docker compose down            # 停止
```

关键设计：构建上下文是父目录（COPY `../nanobot`）；`NANOBOT_SKIP_WEBUI_BUILD=1` 跳过 WebUI；国内镜像（DaoCloud + 清华 pip）；密钥经 `env_file` 注入不打包；SQLite/会话挂卷持久化。

> 注意：RAG（sentence-transformers + 评论索引）目前只在本地，容器未装（torch 较重，详见 `CHALLENGES.md` §6）。

## 文档索引

- 产品需求：`PRD.md`
- 技术栈 + 架构：`技术文档.md`
- 测试方法：`TESTING.md`
- 踩坑记录 + 技术债：`CHALLENGES.md`
- 开发协作规范：`CLAUDE.md`
- Agent 人设：`agent/AGENTS.md`
- 开发流程：`项目流程.md`

## 网络代理（本机）

本机代理 CatBox 监听 `127.0.0.1:7890`，按需开关：`proxy` 开启 / `proxy off` 关闭。
