"""用户偏好工具（F4）。"""

from __future__ import annotations

from typing import Any

from nanobot.agent.tools.base import Tool, ToolResult
from nanobot.agent.tools.context import current_request_context

from mpscb.tools.state import get_preference_store


class GetPreferenceTool(Tool):
    @property
    def name(self) -> str:
        return "get_user_preference"

    @property
    def description(self) -> str:
        return "读取当前用户的某个偏好值（如称呼、语言）。未记录时返回空字符串。"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "偏好键，如 nickname / language"},
            },
            "required": ["key"],
        }

    @property
    def read_only(self) -> bool:
        return True

    async def execute(self, key: str, **_kwargs: Any) -> str:
        store = get_preference_store()
        ctx = current_request_context()
        if store is None or ctx is None or not ctx.sender_id:
            return ToolResult.error("缺少偏好存储或用户上下文")
        return store.get(ctx.sender_id, key) or ""


class SetPreferenceTool(Tool):
    @property
    def name(self) -> str:
        return "set_user_preference"

    @property
    def description(self) -> str:
        return "记录当前用户的某个偏好（如称呼、语言）。"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "偏好键，如 nickname / language"},
                "value": {"type": "string", "description": "偏好值"},
            },
            "required": ["key", "value"],
        }

    async def execute(self, key: str, value: str, **_kwargs: Any) -> str:
        store = get_preference_store()
        ctx = current_request_context()
        if store is None or ctx is None or not ctx.sender_id:
            return ToolResult.error("缺少偏好存储或用户上下文")
        store.set(ctx.sender_id, key, value)
        return f"已记录偏好 {key}={value}"
