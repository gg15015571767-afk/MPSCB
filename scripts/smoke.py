"""冒烟测试：真实 LLM E2E（需 DEEPSEEK_API_KEY，见 .env）。

用法：从项目根目录运行 `python scripts/smoke.py`。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# 让 mpscb-ticket 等 console script 可被 MCP 子进程找到（生产环境用 conda activate 即可）
os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")

from mpscb.app import build_nanobot, init_runtime, run_message
from mpscb.domain.models import Faq
from mpscb.tools import state


def _extract_text(result) -> str:
    # RunResult 形状因版本而异，尽量提取文本
    if hasattr(result, "text"):
        return result.text
    if hasattr(result, "content"):
        return str(result.content)
    return str(result)


async def _run() -> None:
    init_runtime(db_path="data/smoke.db", pref_path="data/smoke_pref.json")
    session_factory = state.get_session_factory()

    with session_factory() as s:
        s.add(Faq(keywords="退款", question="如何退款", answer="7 天内可退"))
        s.commit()

    nanobot = build_nanobot("config.json")
    result = await run_message(
        nanobot,
        "我想申请退款，怎么操作？",
        sender_id="u1",
        session_key="feishu:c1",
    )
    print("=== agent 回复 ===")
    print(_extract_text(result))


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
