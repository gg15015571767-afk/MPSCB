# 开发挑战与踩坑记录

> 记录 MPSCB 项目开发过程中遇到的挑战、根因、解决方案与方法论总结。
> 每个问题按「现象 → 根因 → 解法」组织，末尾提炼可复用的排查方法。

---

## 1. 飞书接入（核心挑战）

### 1.1 机器人能收消息但发送失败（230101）⭐ 最关键

- **现象**：机器人能收到消息（日志触发了 `_on_message`），但回复文字时飞书报 `code=230101: Sending messages to users is temporarily unavailable`，用户只看到 👍 反应、看不到文字。
- **排查过程**：
  1. 看日志 → 确认「接收」正常，卡在「发送」环节（`Failed to send text message: code=230101`）。
  2. 用官方 `lark echo_bot` 样例 + **同一套凭证**测试 → 能发成功，说明 App 权限/发布都没问题。
  3. 对比发现差异：`echo_bot` 用 **`reply` 接口**（回复原消息的 `message_id`），nanobot 默认用 **`create` 接口**（按 `receive_id` 主动发）。
  4. 读 nanobot 源码 `channels/feishu/runtime.py` 确认：只有 `replyToMessage: true` 时才走 reply 接口。
- **根因**：该飞书 App 对单聊是「reply 能发、create 报 230101」；nanobot 默认 create。
- **解法**：`config.json` 加 `"replyToMessage": true`，让 nanobot 改用 reply 接口。
- **方法论**：**用官方样例做对照实验**，快速圈定问题在「环境」还是「框架」；**读源码找开关**，而不是盲目改。

### 1.2 camelCase 别名陷阱

- **现象**：config.json 用 `app_id`/`app_secret`（snake_case），机器人报 `app_id and app_secret not configured`。
- **根因**：nanobot 的 config Base 用 `alias_generator=to_camel`，channel 配置合并默认值时，空的 camelCase 键（`appId`）会**覆盖** snake_case 键（`app_id`）。
- **解法**：channel 配置统一用 camelCase（`appId`/`appSecret`/`allowFrom`/`replyToMessage`）。
- **方法论**：用 `python -c` 做最小验证（`FeishuConfig.model_validate({'app_id':..., 'appId':...})`）确认别名优先级，几十秒定位，而非反复重启。

### 1.3 配对（pairing）阻塞

- **现象**：机器人只回 "Hi! This is your private nanobot." 配对提示，不回客服内容。
- **根因**：nanobot 默认要求用户先审批。
- **解法**：`"allowFrom": ["*"]` 允许所有用户（`channels/base.py` 里 `"*" in allow_list → True`）。
- **方法论**：遇到「默认行为不符合场景」，先找框架的**开关配置**。

### 1.4 流式卡片权限（cardkit）

- **现象**：日志报 `code=99991672`，缺 `cardkit:card:write` 权限。
- **根因**：默认 `streaming: true` 走流式卡片，需要额外权限。
- **解法**：`"streaming": false` 改用纯文本。
- **方法论**：**关掉不需要的高级特性**，降低权限依赖。

### 1.5 config.json 位置

- **现象**：`config.json` 放 workspace（`agent/`）内，报 `session storage must be outside the agent workspace`。
- **根因**：nanobot 的会话存储目录 = config.json 同级 `sessions/`，不能落在 workspace 内。
- **解法**：config.json 移到项目根，`workspace` 仍指向 `agent/`。
- **方法论**：**报错信息往往直接给了方向**（"move --config outside --workspace"）。

### 1.6 工具状态注入缺口（gateway 独立进程）

- **现象**：工具依赖同进程的 `state.init()`（DB 会话工厂 + 偏好存储），但 CLI `nanobot gateway` 是独立进程，工具拿不到依赖。
- **根因**：模块级单例状态 + 独立进程的矛盾。
- **解法**：自定义入口 `scripts/run_bot.py`：先 `init_runtime()` 再 `_run_gateway()`，同进程注入。
- **方法论**：设计入口时**先想清楚进程边界**——「哪些状态必须在同进程」。

### 1.7 密钥泄露风险

- **现象**：真实密钥填进 `.env.example`（git 跟踪文件）。
- **根因**：`.gitignore` 里 `!*.env.example` 把 `.env.example` 白名单放行了。
- **解法**：密钥放 `.env`（gitignore），config.json 用 `${VAR}` 引用（nanobot 原生支持 `${VAR}` 环境变量解析）。
- **方法论**：**提交前审查 `git status`**，确认无密钥；密钥一律走 `.env` + 环境变量引用，不进 git。

### 1.8 钉钉：连接成功但收不到消息（第二平台）

- **现象**：钉钉 Stream 长连接已建立（日志持续收 `ping` 心跳），但用户发消息无任何「Received message」日志、机器人不回。
- **根因**：非代码问题（nanobot 已正确注册 `ChatbotMessage.TOPIC`）；是钉钉后台没推送消息事件——通常是**机器人能力未开启**或**消息权限/版本未发布**。
- **解法**：钉钉后台依次确认 ① 机器人能力已开启；② 开通「企业内机器人发送/接收消息」权限；③ 发布版本并勾选机器人权限；④ 用户在可用范围内。
- **方法论**：**「连得上 ≠ 收得到」**——长连接心跳正常只证明通道通，消息事件是否推送取决于后台的机器人能力与权限配置。

---

## 2. 环境与基础设施

### 2.1 git 代理断连

- **现象**：CatBox 代理没开时，git push 连不上（`Failed to connect to 127.0.0.1 port 7890`）。
- **根因**：git 全局 `http.proxy`/`https.proxy` 写死 7890。
- **解法**：删除全局代理，改用 shell 的 `proxy`/`proxy off` 函数按需开关。

### 2.2 conda channel 失效

- **现象**：`conda create` 报 `HTTP 404`。
- **根因**：`~/.condarc` 里 `pkgs/pro`、`pkgs/free`、`pkgs/msys2` 已失效（付费/废弃/仅 Windows）。
- **解法**：`conda config --remove channels` 删掉失效 channel。

---

## 3. 代码实现

### 3.1 MCP 工具函数名遮蔽

- **现象**：`create_ticket() got multiple values for argument 'title'`。
- **根因**：工具函数 `create_ticket` 与导入的领域函数同名，函数体内递归调用自身。
- **解法**：领域函数加 `_` 前缀别名导入（`from ... import create_ticket as _create_ticket`）。

### 3.2 pytest 收集框架测试

- **现象**：pytest 突然收集了 nanobot 的 6818 个测试，报 `ModuleNotFoundError`。
- **根因**：Bash 工作目录没切回项目根（之前 `cd` 进了 nanobot 目录）。
- **解法**：跑测试/提交前显式 `cd` 回项目根。

---

## 4. 方法论总结

| # | 方法 | 适用场景 |
|---|------|----------|
| 1 | **读源码，不臆造** | 框架行为不确定时，先 grep/读源码确认，再下结论 |
| 2 | **用日志/错误码定位** | 飞书问题靠具体 code（230101、99991672）精确定位，不瞎猜 |
| 3 | **对照实验** | 官方样例 vs 我们的实现对比，快速圈定「环境问题」还是「框架问题」 |
| 4 | **最小验证** | `python -c` 验证假设（如别名优先级），几十秒确认，比反复重启快 |
| 5 | **找开关，不硬改** | 优先找框架配置开关（allowFrom/replyToMessage/streaming），而非改框架源码 |
| 6 | **进程边界** | 设计入口时先想清楚「哪些状态必须在同进程」 |
| 7 | **密钥安全** | 提交前审查 git status；密钥走 .env + `${VAR}` 引用，不进 git |

**核心心法**：遇问题先「分层定位」——是环境、是配置、是框架、还是我们自己的代码？每层都有对应工具（日志、源码、对照样例、最小验证），一层层排除，而不是凭感觉乱试。

---

## 5. 技术债（待处理）

### 5.1 飞书：未能支持 create（主动发消息）接口

- **现状**：为绕过 230101，飞书发送走 `replyToMessage: true`（reply 接口），只能**「回复」用户消息**，不能主动用 **create 接口发起对话**。
- **影响**：
  - 无法主动触达用户（如工单状态更新通知、满意度回访、定时提醒等）。
  - 所有交互都依赖「用户先发消息」，机器人只能被动响应，缺主动推送能力。
- **根因**：该飞书 App 对单聊的 `create` 接口返回 `230101`（确切原因待查：是权限、发布/可用范围，还是飞书对「主动消息」的限制）。
- **待办方向**：
  1. 排查 `create` 场景下 `230101` 的确切触发条件（对照官方文档，确认是否需要单独开通「主动消息」权限）。
  2. 若飞书要求额外权限，去后台申请开通。
  3. 长期：按需在特定场景（如工单闭环通知）用 `create`，其余仍用 `reply`。
