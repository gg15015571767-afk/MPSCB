# 测试说明（如何测试）

> 记录本项目的测试分层、Mock 策略与运行方式。核心原则：**能单测就不集成，能 mock 就不真实**。

---

## 1. 测试分层

| 层 | 内容 | 需外部依赖 | 位置 |
|----|------|-----------|------|
| 单元测试 | 数据模型、领域服务、工具、MCP、配置 | ❌ | `tests/test_*.py` |
| 集成测试 | 工具 + MCP + 领域 + 数据闭环 | ❌ | `tests/test_e2e.py` |
| payload 解析 | 飞书消息事件格式 + 解析 | ❌ | `tests/test_feishu_payload.py` |
| 冒烟测试 | 真实 DeepSeek LLM 调工具 | ✅ `DEEPSEEK_API_KEY` | `scripts/smoke.py` |
| 真实环境 | 真实飞书收发 | ✅ 飞书 App | `scripts/run_bot.py` |

---

## 2. 运行命令

```bash
conda activate mpscb

# 全部单测 + 集成测试（36 个，秒级）
python -m pytest

# 冒烟测试（真实 LLM，需 .env 里的 DEEPSEEK_API_KEY）
python scripts/smoke.py

# 真实飞书（需 .env 的飞书凭证 + 已发布版本，Ctrl+C 停止）
python scripts/run_bot.py
```

---

## 3. Mock 策略（关键）

| 外部依赖 | 如何 mock | 位置 |
|---------|----------|------|
| 数据库 | 内存 SQLite（`sqlite://` + `StaticPool`），每个测试独立不落盘 | `tests/conftest.py` |
| 飞书事件 | 真实 `im.message.receive_v1` 格式的 JSON fixture | `tests/fixtures/feishu_message_event.json` |
| 用户上下文 | `request_context(RequestContext(sender_id=...))` 绑定，不用真实飞书 | 工具测试里 |
| 工单 MCP 进程 | `build_mcp(session_factory)` + `call_tool(...)` 直接调函数，不起 stdio 子进程 | `tests/test_mcp_server.py` |
| DeepSeek LLM | 单测全程不调；只在 `smoke.py` 用真实 key | — |
| 飞书传输 | 单测全程不连；只在 `run_bot.py` 用真实 App | — |

---

## 4. 各模块测试要点

- **数据模型**（`test_models.py`）：内存 SQLite CRUD + 唯一约束（`IntegrityError`）+ 状态更新。
- **领域服务**（`test_ticket_service.py` 等）：工单号生成唯一性、FAQ 精确/关键词匹配优先级、反馈参数校验。
- **工具层**（`test_tools.py`）：`state.init()` 注入 session_factory/偏好存储 → `request_context` 绑定 sender_id → `asyncio.run` 执行 `execute`；另验证 entry_points 注册。
- **工单 MCP**（`test_mcp_server.py`）：`build_mcp` + `call_tool` 不起了进程；`_text()` 处理返回的 `(content_blocks, structured)` 元组。
- **配置**（`test_config.py`）：`load_config` 校验 provider/model/workspace/mcp_servers。
- **E2E**（`test_e2e.py`）：`init_runtime` 统一注入，走 FAQ命中→问题记录→MCP建单转人工→反馈 完整闭环，验证四张表一致。
- **飞书 payload**（`test_feishu_payload.py`）：校验 p2p/text 格式、`ou_`/`oc_` 前缀、`content`(JSON 字符串) → 文本 → FAQ 匹配。

---

## 5. 测试方法论

1. **测试驱动**：每写完一个模块立即配套 pytest（呼应 `项目流程.md` Step 9）。
2. **分层隔离**：先单测（纯逻辑），再集成（多模块），最后冒烟/真实环境。
3. **Mock 一切外部**：LLM、飞书、MCP 进程、数据库，单测里全部可控替代，保证秒级、可重复。
4. **真实环境单独跑**：真实 DeepSeek/飞书只放进 `smoke.py` / `run_bot.py`，不进 pytest（避免测试依赖网络和凭证）。
5. **fixture 即文档**：飞书 payload fixture 既是测试数据，也是外部接口格式的活文档。
