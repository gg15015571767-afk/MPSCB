"""数据模型 CRUD 测试。"""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from mpscb.domain.models import Faq, Feedback, QuestionRecord, Ticket


def test_ticket_crud(session):
    t = Ticket(
        ticket_no="TK-20260914-0001",
        title="无法登录",
        description="用户反馈无法登录",
        user_id="u1",
        channel="feishu",
    )
    session.add(t)
    session.commit()

    got = session.query(Ticket).filter_by(ticket_no="TK-20260914-0001").one()
    assert got.user_id == "u1"
    assert got.status == "pending"


def test_ticket_no_unique(session):
    session.add(Ticket(ticket_no="TK-1", title="a", description="d", user_id="u1"))
    session.add(Ticket(ticket_no="TK-1", title="b", description="d", user_id="u2"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_ticket_status_update(session):
    t = Ticket(ticket_no="TK-2", title="a", description="d", user_id="u1")
    session.add(t)
    session.commit()
    t.status = "waiting_human"
    session.commit()
    assert session.query(Ticket).one().status == "waiting_human"


def test_faq_crud(session):
    faq = Faq(keywords="登录,密码", question="登录失败怎么办", answer="请重置密码", category="账号")
    session.add(faq)
    session.commit()
    got = session.query(Faq).one()
    assert got.keywords == "登录,密码"
    assert got.category == "账号"


def test_question_record(session):
    r = QuestionRecord(user_id="u1", question="怎么改密码", resolution="faq_hit", faq_id=1)
    session.add(r)
    session.commit()
    got = session.query(QuestionRecord).one()
    assert got.resolution == "faq_hit"


def test_feedback(session):
    f = Feedback(user_id="u1", session_id="feishu:chat1", rating="satisfied")
    session.add(f)
    session.commit()
    got = session.query(Feedback).one()
    assert got.rating == "satisfied"
