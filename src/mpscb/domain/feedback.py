"""满意度反馈领域服务。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from mpscb.domain.models import RATINGS, Feedback


def record_feedback(
    session: Session,
    *,
    user_id: str,
    rating: str,
    session_id: str | None = None,
    ticket_id: int | None = None,
    comment: str | None = None,
) -> Feedback:
    if rating not in RATINGS:
        raise ValueError(f"非法评分: {rating}")
    f = Feedback(
        user_id=user_id,
        session_id=session_id,
        ticket_id=ticket_id,
        rating=rating,
        comment=comment,
    )
    session.add(f)
    session.commit()
    return f
