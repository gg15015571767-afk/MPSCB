"""问题记录工具（F5）。"""

from __future__ import annotations

from typing import Any

from nanobot.agent.tools.base import Tool, ToolResult
from nanobot.agent.tools.context import current_request_context

from mpscb.domain.models import RESOLUTIONS, QuestionRecord
from mpscb.tools.state import get_session_factory


class RecordQuestionTool(Tool):
    @property
    def name(self) -> str:
        return "record_question"

    @property
    def description(self) -> str:
        return (
            "记录一次用户提问及处理路径，用于审计追溯。"
            f"resolution 取值：{' / '.join(RESOLUTIONS)}。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "用户问题原文"},
                "resolution": {
                    "type": "string",
                    "enum": list(RESOLUTIONS),
                    "description": "处理路径",
                },
            },
            "required": ["question", "resolution"],
        }

    async def execute(self, question: str, resolution: str, **_kwargs: Any) -> str:
        if resolution not in RESOLUTIONS:
            return ToolResult.error(f"非法处理路径: {resolution}")
        factory = get_session_factory()
        if factory is None:
            return ToolResult.error("工具未初始化：缺少数据库会话工厂")
        ctx = current_request_context()
        with factory() as session:
            session.add(
                QuestionRecord(
                    user_id=ctx.sender_id if ctx and ctx.sender_id else "",
                    channel=ctx.channel if ctx else "feishu",
                    question=question,
                    resolution=resolution,
                )
            )
            session.commit()
        return "已记录问题"
