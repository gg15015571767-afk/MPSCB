"""评论 RAG 检索测试（mock embedding，测试建索引 + 检索逻辑）。"""

from __future__ import annotations

from mpscb.domain import review_rag


def _fake_embed(texts):
    # 含 'small' → [1,0]；含 'soft' → [0,1]；其他 → [0,0]
    def vec(t):
        tl = t.lower()
        if "small" in tl:
            return [1.0, 0.0]
        if "soft" in tl:
            return [0.0, 1.0]
        return [0.0, 0.0]

    return [vec(t) for t in texts]


def test_build_and_retrieve(monkeypatch, tmp_path):
    monkeypatch.setattr(review_rag, "embed", _fake_embed)
    reviews = [
        {"text": "this dress runs small", "department": "Dresses"},
        {"text": "the fabric is soft", "department": "Tops"},
    ]
    assert review_rag.build_index(reviews, tmp_path) == 2

    results = review_rag.retrieve("does it run small", tmp_path, top_k=1)
    assert results[0]["department"] == "Dresses"
    assert results[0]["score"] == 1.0
