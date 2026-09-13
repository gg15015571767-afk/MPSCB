# CLAUDE.md — AI 协作开发规范

> 本文件面向**开发协作**：指导 Claude Code 如何在本仓库开发 MPSCB 项目。
> 运行时 agent 的人设与系统信息在 [`agent/AGENTS.md`](agent/AGENTS.md)，两者职责不同。

## 项目概览

MPSCB 是基于 **Nanobot** 的智能客服系统：经飞书等 IM 平台回答 FAQ、创建/查询工单、记录偏好、收集满意度。首期本地单实例 + 飞书单平台。

## 先读这些文档

- 需求：`PRD.md`
- 技术栈 + 架构：`技术文档.md`
- 流程：`项目流程.md`
- **运行时 agent 人设 + 系统信息：`agent/AGENTS.md`**（动业务代码前先读——你开发的 agent 是智能客服）

## 开发环境

- **虚拟环境**：conda env `mpscb`（Python 3.11）
- **网络代理**：`proxy` 开 / `proxy off` 关（CatBox 7890，默认直连；需要走代理的命令在同一条命令里临时 `export`）
- **框架**：`../nanobot`（外部依赖，勿修改框架源码）

## 目录结构

```
MPSCB/
├── CLAUDE.md                 # 本文件：AI 协作开发规范
├── agent/                    # nanobot agent 位置
│   ├── AGENTS.md             # 智能客服人设 + 系统信息
│   ├── prompt/               # system prompt
│   └── config/               # nanobot 配置（provider/channel/mcp）
├── PRD.md / 技术文档.md / 项目流程.md
├── src/mpscb/                # 业务代码（domain / mcp_server / tools）
├── data/                     # 运行时数据（*.db、MEMORY.md）
└── tests/                    # pytest
```

## 开发约定

- **命名**：模块/函数/变量 `snake_case`；类 `PascalCase`；常量 `UPPER_SNAKE_CASE`；SQLAlchemy 模型类名单数、表名复数
- **类型标注**：所有函数签名带类型注解（Python 3.11）
- **分层边界**：工具层 → 领域服务层 → 数据层；工具层不直接碰 DB 引擎
- **配置外置**：API Key / 凭据走环境变量或 nanobot 配置，禁止硬编码
- **测试**：每个模块配套 pytest（工单 MCP 工具与消息转换逻辑必须有单测）
- **日志**：统一 `loguru`，敏感信息脱敏

## 关键提醒

你开发的运行时 agent 是**智能客服**（人设见 `agent/AGENTS.md`），业务逻辑只服务 PRD 七项职责，不引入通用助手能力。
