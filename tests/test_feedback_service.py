"""满意度反馈服务测试。"""

from __future__ import annotations

import pytest

from mpscb.domain.feedback import record_feedback


def test_record_feedback(session):
    f = record_feedback(session, user_id="u1", rating="5", session_id="feishu:chat1")
    assert f.rating == "5"
    assert f.session_id == "feishu:chat1"


def test_record_feedback_invalid(session):
    with pytest.raises(ValueError):
        record_feedback(session, user_id="u1", rating="6")
