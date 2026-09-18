"""应用入口：串联各层（DB + 偏好存储 + 工具状态 + nanobot 运行时）。"""

from __future__ import annotations

import os

from mpscb.domain.db import create_engine_for_db, make_session_factory
from mpscb.domain.preference import SqlPreferenceStore
from mpscb.tools import state

DEFAULT_DB = "data/mpscb.db"


def init_runtime(db_path: str | None = None):
    """初始化业务运行时：加载 .env → DB 引擎 + 偏好存储，并注入工具层单例。

    必须在启动 nanobot agent（同进程）之前调用，工具才能拿到 DB/偏好依赖。
    """
    from dotenv import load_dotenv

    load_dotenv()  # 加载项目根 .env（DEEPSEEK_API_KEY / FEISHU_* / MPSCB_*）
    db = db_path or os.environ.get("MPSCB_DB", DEFAULT_DB)
    engine = create_engine_for_db(db)
    session_factory = make_session_factory(engine)
    preference_store = SqlPreferenceStore(session_factory)  # 偏好存 SQLite（与业务同库）
    state.init(session_factory=session_factory, preference_store=preference_store)
    return session_factory, preference_store


def build_nanobot(config_path: str = "config.json"):
    """从 config.json 构建 Nanobot SDK 实例（需 DEEPSEEK_API_KEY 才能 run）。"""
    from nanobot import Nanobot

    return Nanobot.from_config(config_path)


async def run_message(
    nanobot,
    message: str,
    *,
    sender_id: str,
    session_key: str,
    channel: str = "feishu",
    chat_id: str | None = None,
):
    """处理一条用户消息（SDK 方式，供 E2E 调试 / 无渠道场景）。"""
    return await nanobot.run(
        message,
        sender_id=sender_id,
        session_key=session_key,
        channel=channel,
        chat_id=chat_id or sender_id,
    )


def main() -> None:
    """启动入口：先注入工具状态，再交给 nanobot。

    注意：工具层依赖本进程内的 state 单例，因此生产运行需在**同一进程**先
    `init_runtime()` 再启动 agent（SDK 方式）。CLI `nanobot gateway` 是独立进程，
    需额外注入机制（见 README「运行」）；本地联调可先用 `run_message` 走 SDK。
    """
    init_runtime()
    print("业务运行时已初始化（DB + 偏好存储 + 工具状态）")


if __name__ == "__main__":
    main()
