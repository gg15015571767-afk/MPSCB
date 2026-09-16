"""评论检索工具（RAG 生成）。"""

from __future__ import annotations

import os
from typing import Any

from nanobot.agent.tools.base import Tool, ToolResult

from mpscb.domain.review_rag import retrieve

INDEX_DIR = os.environ.get("MPSCB_REVIEW_INDEX", "data/review_index")


class SearchReviewsTool(Tool):
    @property
    def name(self) -> str:
        return "search_reviews"

    @property
    def description(self) -> str:
        return (
            "检索与用户问题语义最相关的商品评论（向量检索 top-5），"
            "用于回答 FAQ 知识库之外的具体商品问题（尺码、面料、色差、质量等）。"
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
            reviews = retrieve(question, INDEX_DIR, top_k=5)
        except FileNotFoundError:
            return ToolResult.error("评论索引不存在，请先运行 scripts/build_review_index.py")
        if not reviews:
            return "未找到相关评论"
        return "\n".join(
            f"- [{r['score']:.2f}] ({r['department']}, {r['rating']}★) {r['text']}"
            for r in reviews
        )
