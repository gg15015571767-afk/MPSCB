"""电信问答检索工具（RAG）。"""

from __future__ import annotations

import os
from typing import Any

from nanobot.agent.tools.base import Tool, ToolResult

from mpscb.domain.review_rag import retrieve

INDEX_DIR = os.environ.get("MPSCB_QA_INDEX", "data/qa_index")


class SearchQaTool(Tool):
    @property
    def name(self) -> str:
        return "search_qa"

    @property
    def description(self) -> str:
        return (
            "在电信问答知识库（9 万条）中检索与用户问题语义最相关的问题及最佳回答（top-3），"
            "用于回答宽带、话费、流量、套餐、积分、补卡、故障等问题。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "用户的问题"},
            },
            "required": ["question"],
        }

    @property
    def read_only(self) -> bool:
        return True

    async def execute(self, question: str, **_kwargs: Any) -> str:
        try:
            results = retrieve(question, INDEX_DIR, top_k=3)
        except FileNotFoundError:
            return ToolResult.error("问答索引不存在，请先构建（scripts/eval_retrieval.py）")
        if not results:
            return "未找到相关回答"
        return "\n".join(
            f"- [{r['score']:.2f}] Q: {r['text']}\n  A: {r['answer']}" for r in results
        )
