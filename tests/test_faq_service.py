"""FAQ 匹配服务测试。"""

from __future__ import annotations

from mpscb.domain.faq import match_faq
from mpscb.domain.models import Faq


def _seed(session):
    session.add(Faq(keywords="登录,密码", question="登录失败怎么办", answer="请重置密码"))
    session.add(Faq(keywords="退款", question="如何退款", answer="7 天内可退"))
    session.commit()


def test_exact_match(session):
    _seed(session)
    got = match_faq(session, "登录失败怎么办")
    assert got is not None and got.answer == "请重置密码"


def test_keyword_match(session):
    _seed(session)
    got = match_faq(session, "我忘了密码没法登录")
    assert got is not None and "重置密码" in got.answer


def test_no_match(session):
    _seed(session)
    assert match_faq(session, "今天天气如何") is None


def test_empty_question(session):
    _seed(session)
    assert match_faq(session, "   ") is None
