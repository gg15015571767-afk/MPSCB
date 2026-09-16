"""评论检索工具测试（mock retrieve）。"""

from __future__ import annotations

import asyncio

from mpscb.tools.review_tool import SearchReviewsTool


def test_search_reviews(monkeypatch):
    monkeypatch.setattr(
        "mpscb.tools.review_tool.retrieve",
        lambda q, d, top_k=5: [
            {"text": "this dress runs small", "department": "Dresses", "rating": "3", "score": 0.86},
        ],
    )
    result = asyncio.run(SearchReviewsTool().execute(question="does it run small?"))
    assert "runs small" in result
    assert "Dresses" in result


def test_search_reviews_missing_index(monkeypatch):
    def _raise(q, d, top_k=5):
        raise FileNotFoundError("no index")

    monkeypatch.setattr("mpscb.tools.review_tool.retrieve", _raise)
    result = asyncio.run(SearchReviewsTool().execute(question="does it run small?"))
    assert "评论索引不存在" in result
