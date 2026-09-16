# MPSCB — 智能客服系统

基于 **Nanobot** 框架的智能客服机器人：经飞书等 IM 平台回答 FAQ、创建/查询工单、记录用户偏好、收集满意度反馈，替人工客服处理简单、重复性问题。

> **当前状态**：文档与架构已定稿（Step 1–6 完成），代码实现待 Step 8。本仓库目前为设计文档 + 目录骨架，**尚无可运行代码**。

---

## 功能特性（PRD 七项）

1. **FAQ 查询** —— 关键词匹配 → DeepSeek 兜底 → 转人工 三级策略
2. **工单创建** —— 落库并返回工单号
3. **工单查询** —— 凭工单号查状态
4. **用户偏好记忆** —— 记录并引用称呼/语言等偏好
5. **问题记录** —— 每次问答留痕可追溯
6. **问题转人工** —— 兜底失败/用户要求时标「待人工」
7. **满意度反馈** —— 解决后主动收集

## 技术栈

| 层 | 选型 |
|----|------|
| Agent 框架 | Nanobot（`../nanobot`） |
| 语言 | Python 3.11 |
| 数据存储 | SQLite（业务）+ 文件/Redis（偏好，可切换） |
| AI 模型 | DeepSeek API（openai_compat 后端） |
| 接入平台 | 飞书 + 钉钉 |
| 部署 | Docker / Docker Compose（V1.2） |

## 目录结构

```
MPSCB/
├── CLAUDE.md            # AI 协作开发规范
├── agent/               # nanobot agent（即 workspace）
│   ├── SOUL.md          # 智能客服人设
│   ├── AGENTS.md        # 客服行为规范
│   ├── memory/          # 长期记忆
│   └── config.json      # nanobot 配置
├── PRD.md / 技术文档.md / 项目流程.md
├── src/mpscb/           # 业务代码
└── tests/               # pytest
```

## 快速开始（Step 8 实现后可用）

### 1. 环境准备

```bash
conda create -n mpscb python=3.11 -y
conda activate mpscb
```

### 2. 安装 Nanobot 依赖

```bash
pip install -e ../nanobot
```

### 3. 配置

- 设置环境变量：`DEEPSEEK_API_KEY`
- 飞书开放平台创建应用，获取 App ID / App Secret（本地开发可用长连接模式，无需公网域名）
- 编写 `agent/config.json`（DeepSeek provider + 飞书 channel + 工单 MCP server + workspace 指向 `agent/`）

### 4. 运行

```bash
nanobot gateway --config agent/config.json
# 或 Python SDK：Nanobot.from_config(config_path="agent/config.json")
```

## 配置要点

| 配置 | 说明 |
|------|------|
| `providers` | DeepSeek（`DEEPSEEK_API_KEY` + `api.deepseek.com`） |
| `channels` | 飞书、钉钉（长连接） |
| `agents.workspace` | 指向 `agent/`（含 SOUL.md / AGENTS.md / memory） |
| `tools.mcp_servers` | 工单 MCP Server（stdio） |
| `preference.backend` | `file`（V1.0）→ `redis`（V1.2） |

## Docker 部署（V1.2）

```bash
# 前提：已安装并启动 Docker Desktop
cd ~/CODE/NanobotProject/MPSCB
docker compose up -d --build   # 构建并后台启动
docker compose logs -f         # 查看日志
docker compose down            # 停止
```

关键设计：
- **构建上下文是父目录**（`context: ..`），因为要 COPY 本地 `../nanobot`（领先 PyPI 0.3.0）。
- **跳过 WebUI 打包**：`NANOBOT_SKIP_WEBUI_BUILD=1`（机器人无需 WebUI）。
- **国内镜像**：基础镜像 DaoCloud、pip 清华镜像（部署到国外服务器时换回官方源）。
- 密钥从 `.env` 经 `env_file` 注入，**不打包进镜像**。
- SQLite 数据、会话状态挂到 `mpscb-data` / `mpscb-sessions` 卷，容器重启不丢；`restart: unless-stopped` 崩溃自动拉起。

## 文档索引

- 产品需求：`PRD.md`
- 技术栈 + 架构：`技术文档.md`
- 开发协作规范：`CLAUDE.md`
- Agent 人设 + 系统信息：`agent/AGENTS.md`
- 开发流程：`项目流程.md`
- 测试方法：`TESTING.md`
- 踩坑记录 + 技术债：`CHALLENGES.md`

## 网络代理（本机）

本机代理 CatBox 监听 `127.0.0.1:7890`，按需开关：`proxy` 开启 / `proxy off` 关闭。
