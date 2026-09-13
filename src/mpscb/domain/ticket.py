"""工单领域服务。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mpscb.domain.models import TICKET_STATUSES, Ticket


def _gen_ticket_no(session: Session) -> str:
    """生成工单号 TK-YYYYMMDD-XXXX（单实例下唯一；多实例见技术文档 §11.10）。"""
    prefix = f"TK-{datetime.utcnow():%Y%m%d}-"
    count = session.scalar(
        select(func.count())
        .select_from(Ticket)
        .where(Ticket.ticket_no.like(f"{prefix}%"))
    ) or 0
    return f"{prefix}{count + 1:04d}"


def create_ticket(
    session: Session,
    *,
    title: str,
    description: str,
    user_id: str,
    channel: str = "feishu",
    session_id: str | None = None,
) -> Ticket:
    t = Ticket(
        ticket_no=_gen_ticket_no(session),
        title=title,
        description=description,
        user_id=user_id,
        channel=channel,
        session_id=session_id,
    )
    session.add(t)
    session.commit()
    return t


def get_ticket(session: Session, ticket_no: str) -> Ticket | None:
    return session.scalar(select(Ticket).where(Ticket.ticket_no == ticket_no))


def update_status(session: Session, ticket_no: str, status: str) -> Ticket | None:
    if status not in TICKET_STATUSES:
        raise ValueError(f"非法工单状态: {status}")
    t = get_ticket(session, ticket_no)
    if t is None:
        return None
    t.status = status
    session.commit()
    return t


def list_tickets(session: Session, user_id: str) -> list[Ticket]:
    return list(
        session.scalars(
            select(Ticket).where(Ticket.user_id == user_id).order_by(Ticket.id.desc())
        )
    )
