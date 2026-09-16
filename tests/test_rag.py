"""RAG 语义匹配测试（mock embedding，测试相似度逻辑 + match_faq 集成）。"""

from __future__ import annotations

from mpscb.domain import faq as faq_service
from mpscb.domain import rag
from mpscb.domain.models import Faq


def _fake_embed(texts):
    # 简单 fake：含 'size'/'tight' → [1,0]；含 'see'/'transparent' → [0,1]；其他 → [0,0]
    def vec(t):
        tl = t.lower()
        if "size" in tl or "tight" in tl:
            return [1.0, 0.0]
        if "see" in tl or "transparent" in tl:
            return [0.0, 1.0]
        return [0.0, 0.0]

    return [vec(t) for t in texts]


def test_semantic_match_hit(monkeypatch):
    monkeypatch.setattr(rag, "embed", _fake_embed)
    hit = rag.semantic_match("will this be too tight?", ["Do your clothes run true to size?"], threshold=0.5)
    assert hit is not None
    assert hit[0] == 0 and hit[1] == 1.0


def test_semantic_match_no_hit(monkeypatch):
    monkeypatch.setattr(rag, "embed", _fake_embed)
    hit = rag.semantic_match("completely unrelated", ["Do your clothes run true to size?"], threshold=0.5)
    assert hit is None


def test_match_faq_semantic_fallback(monkeypatch, session):
    # FAQ 无关键词，精确也不匹配 → 走语义层
    session.add(Faq(question="Do your clothes run true to size?", answer="true to size", keywords=""))
    session.commit()
    monkeypatch.setattr(rag, "embed", _fake_embed)
    got = faq_service.match_faq(session, "will this be too tight on me?")
    assert got is not None
    assert "true to size" in got.answer
