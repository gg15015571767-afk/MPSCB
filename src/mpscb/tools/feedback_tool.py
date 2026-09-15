"""满意度反馈工具（F7）。"""

from __future__ import annotations

from typing import Any

from nanobot.agent.tools.base import Tool, ToolResult
from nanobot.agent.tools.context import current_request_context

from mpscb.domain.feedback import record_feedback
from mpscb.domain.models import RATINGS
from mpscb.tools.state import get_session_factory


class RecordFeedbackTool(Tool):
    @property
    def name(self) -> str:
        return "record_feedback"

    @property
    def description(self) -> str:
        return "记录用户满意度反馈（1-5 星，5 最好）。rating 取值：1 到 5。"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "rating": {"type": "string", "enum": list(RATINGS), "description": "满意度"},
                "comment": {"type": "string", "description": "可选备注"},
            },
            "required": ["rating"],
        }

    async def execute(self, rating: str, comment: str | None = None, **_kwargs: Any) -> str:
        factory = get_session_factory()
        if factory is None:
            return ToolResult.error("工具未初始化：缺少数据库会话工厂")
        ctx = current_request_context()
        with factory() as session:
            record_feedback(
                session,
                user_id=ctx.sender_id if ctx and ctx.sender_id else "",
                rating=rating,
                session_id=ctx.session_key if ctx else None,
                comment=comment,
            )
        return "已记录反馈"
