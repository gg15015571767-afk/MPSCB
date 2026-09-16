"""运营统计测试。"""

from __future__ import annotations

from mpscb.domain import stats as stats_service
from mpscb.domain.models import Feedback, QuestionRecord


def test_faq_hit_rate(session):
    session.add_all(
        [
            QuestionRecord(user_id="u1", question="a", resolution="faq_hit"),
            QuestionRecord(user_id="u2", question="b", resolution="faq_hit"),
            QuestionRecord(user_id="u3", question="c", resolution="llm_fallback"),
            QuestionRecord(user_id="u4", question="d", resolution="human"),
        ]
    )
    session.commit()
    counts = stats_service.count_questions_by_resolution(session)
    assert counts == {"faq_hit": 2, "llm_fallback": 1, "human": 1}
    assert stats_service.faq_hit_rate(session) == 0.5


def test_faq_hit_rate_empty(session):
    assert stats_service.faq_hit_rate(session) is None


def test_average_rating(session):
    session.add_all(
        [Feedback(user_id="u1", rating="5"), Feedback(user_id="u2", rating="4"), Feedback(user_id="u3", rating="3")]
    )
    session.commit()
    assert stats_service.count_feedbacks_by_rating(session) == {"5": 1, "4": 1, "3": 1}
    assert stats_service.average_rating(session) == 4.0
