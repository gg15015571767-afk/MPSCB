"""FAQ 匹配领域服务（V1.0 关键词/精确匹配，不引入向量库）。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from mpscb.domain.models import Faq


def match_faq(session: Session, question: str) -> Faq | None:
    """三级策略的第 1 级：精确问法 → 关键词包含匹配。命中返回 Faq，否则 None。"""
    q = (question or "").strip()
    if not q:
        return None

    faqs = list(session.scalars(select(Faq)))

    # 1) 精确匹配标准问法
    for f in faqs:
        if (f.question or "").strip() == q:
            return f

    # 2) 关键词包含匹配
    for f in faqs:
        for kw in (f.keywords or "").split(","):
            kw = kw.strip()
            if kw and kw in q:
                return f

    return None
