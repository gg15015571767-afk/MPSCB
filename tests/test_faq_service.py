"""FAQ 匹配服务测试。"""

from __future__ import annotations

from mpscb.domain.faq import match_faq
from mpscb.domain.models import Faq


def _seed(session):
    session.add(Faq(keywords="宽带,网速,测速", question="电信宽带网速怎么测？", answer="登录电信网厅测速"))
    session.add(Faq(keywords="话费,查询,余额", question="怎么查询电信话费？", answer="发短信或登录网厅查询"))
    session.commit()


def test_exact_match(session):
    _seed(session)
    got = match_faq(session, "电信宽带网速怎么测？")
    assert got is not None and got.answer == "登录电信网厅测速"


def test_keyword_match(session):
    _seed(session)
    got = match_faq(session, "我想查一下宽带网速")
    assert got is not None and "测速" in got.answer


def test_no_match(session):
    _seed(session)
    assert match_faq(session, "如何做红烧肉") is None


def test_empty_question(session):
    _seed(session)
    assert match_faq(session, "   ") is None
