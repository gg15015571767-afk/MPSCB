"""运营统计（运维观测）：命中率、满意度等聚合。"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mpscb.domain.models import Feedback, QuestionRecord


def count_questions_by_resolution(session: Session) -> dict[str, int]:
    """问题处理路径分布（faq_hit / llm_fallback / human）。"""
    rows = session.execute(
        select(QuestionRecord.resolution, func.count()).group_by(QuestionRecord.resolution)
    ).all()
    return {res: cnt for res, cnt in rows}


def faq_hit_rate(session: Session) -> float | None:
    """FAQ 命中率 = faq_hit / 全部问题；无数据返回 None。"""
    counts = count_questions_by_resolution(session)
    total = sum(counts.values())
    if total == 0:
        return None
    return counts.get("faq_hit", 0) / total


def count_feedbacks_by_rating(session: Session) -> dict[str, int]:
    """满意度分布（1-5 星）。"""
    rows = session.execute(
        select(Feedback.rating, func.count()).group_by(Feedback.rating)
    ).all()
    return {rating: cnt for rating, cnt in rows}


def average_rating(session: Session) -> float | None:
    """平均满意度（1-5 星），无数据返回 None。"""
    ratings = [int(r) for r in session.scalars(select(Feedback.rating))]
    if not ratings:
        return None
    return sum(ratings) / len(ratings)


def unanswered_questions(session: Session, top_n: int = 10) -> list[tuple[str, int]]:
    """高频未命中问题（resolution != faq_hit），按频次降序，作为「建议补 FAQ」的候选。"""
    rows = session.execute(
        select(QuestionRecord.question, func.count())
        .where(QuestionRecord.resolution != "faq_hit")
        .group_by(QuestionRecord.question)
        .order_by(func.count().desc())
        .limit(top_n)
    ).all()
    return [(q, cnt) for q, cnt in rows]
