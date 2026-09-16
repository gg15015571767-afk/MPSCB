"""FAQ 匹配服务测试。"""

from __future__ import annotations

from mpscb.domain.faq import match_faq
from mpscb.domain.models import Faq


def _seed(session):
    session.add(Faq(keywords="login,password", question="How do I reset my password?", answer="Use the forgot password link"))
    session.add(Faq(keywords="refund", question="How do I get a refund?", answer="Refunds within 7 days"))
    session.commit()


def test_exact_match(session):
    _seed(session)
    got = match_faq(session, "How do I reset my password?")
    assert got is not None and got.answer == "Use the forgot password link"


def test_keyword_match(session):
    _seed(session)
    got = match_faq(session, "I forgot my password and can't log in")
    assert got is not None and "forgot password" in got.answer


def test_no_match(session):
    _seed(session)
    assert match_faq(session, "What is the capital of France?") is None


def test_empty_question(session):
    _seed(session)
    assert match_faq(session, "   ") is None
