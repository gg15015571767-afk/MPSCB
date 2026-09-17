"""电信问答检索工具测试（mock retrieve）。"""

from __future__ import annotations

import asyncio

from mpscb.tools.qa_tool import SearchQaTool


def test_search_qa(monkeypatch):
    monkeypatch.setattr(
        "mpscb.tools.qa_tool.retrieve",
        lambda q, d, top_k=3: [
            {"text": "电信宽带怎么测速", "answer": "登录网厅测速", "score": 0.95},
        ],
    )
    result = asyncio.run(SearchQaTool().execute(question="怎么测宽带网速"))
    assert "测速" in result


def test_search_qa_missing_index(monkeypatch):
    def _raise(q, d, top_k=3):
        raise FileNotFoundError("no index")

    monkeypatch.setattr("mpscb.tools.qa_tool.retrieve", _raise)
    result = asyncio.run(SearchQaTool().execute(question="怎么测网速"))
    assert "索引不存在" in result
