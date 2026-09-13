"""FAQ 匹配工具（F1）。"""

from __future__ import annotations

from typing import Any

from nanobot.agent.tools.base import Tool, ToolResult

from mpscb.domain.faq import match_faq
from mpscb.tools.state import get_session_factory


class MatchFaqTool(Tool):
    @property
    def name(self) -> str:
        return "match_faq"

    @property
    def description(self) -> str:
        return (
            "在 FAQ 知识库中精确/关键词匹配用户问题。"
            "命中返回标准答案；未命中返回 NO_MATCH（此时应改用 LLM 兜底或转人工）。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "用户问题原文"},
            },
            "required": ["question"],
        }

    @property
    def read_only(self) -> bool:
        return True

    async def execute(self, question: str, **_kwargs: Any) -> str:
        factory = get_session_factory()
        if factory is None:
            return ToolResult.error("工具未初始化：缺少数据库会话工厂")
        with factory() as session:
            faq = match_faq(session, question)
            return faq.answer if faq else "NO_MATCH"
