"""FAQ 匹配领域服务（V1.0 关键词/精确匹配，不引入向量库）。"""

from __future__ import annotations

from sqlalchemy import delete, select
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


def add_faq(
    session: Session,
    *,
    question: str,
    answer: str,
    keywords: str = "",
    category: str | None = None,
) -> Faq:
    faq = Faq(question=question, answer=answer, keywords=keywords, category=category)
    session.add(faq)
    session.commit()
    return faq


def list_faqs(session: Session) -> list[Faq]:
    return list(session.scalars(select(Faq).order_by(Faq.id)))


def delete_faq(session: Session, faq_id: int) -> bool:
    faq = session.get(Faq, faq_id)
    if faq is None:
        return False
    session.delete(faq)
    session.commit()
    return True


def import_faqs(session: Session, items: list[dict]) -> int:
    """批量导入 FAQ（items 为 [{question, answer, keywords?, category?}, ...]），返回导入条数。"""
    count = 0
    for item in items:
        session.add(
            Faq(
                question=item["question"],
                answer=item["answer"],
                keywords=item.get("keywords", ""),
                category=item.get("category"),
            )
        )
        count += 1
    session.commit()
    return count


def clear_faqs(session: Session) -> int:
    """清空所有 FAQ，返回删除条数。"""
    n = len(list_faqs(session))
    session.execute(delete(Faq))
    session.commit()
    return n
