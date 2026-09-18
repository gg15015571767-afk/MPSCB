"""工具层测试（直接调用 execute，绑定 RequestContext 提供 sender_id）。"""

from __future__ import annotations

import asyncio
from importlib.metadata import entry_points

import pytest

from nanobot.agent.tools.context import RequestContext, request_context

from mpscb.domain.models import Faq, Feedback, QuestionRecord
from mpscb.domain.preference import SqlPreferenceStore
from mpscb.tools import state
from mpscb.tools.faq_tool import MatchFaqTool
from mpscb.tools.feedback_tool import RecordFeedbackTool
from mpscb.tools.preference_tool import GetPreferenceTool, SetPreferenceTool
from mpscb.tools.question_tool import RecordQuestionTool


@pytest.fixture
def ctx():
    return RequestContext(
        channel="feishu", chat_id="chat1", sender_id="u1", session_key="feishu:chat1"
    )


@pytest.fixture
def store(session_factory):
    return SqlPreferenceStore(session_factory)


@pytest.fixture
def setup(session_factory, store):
    state.init(session_factory=session_factory, preference_store=store)


async def _execute(tool, ctx, **kwargs):
    with request_context(ctx):
        return await tool.execute(**kwargs)


def run(tool, ctx, **kwargs):
    return asyncio.run(_execute(tool, ctx, **kwargs))


def test_match_faq_hit(session_factory, store, ctx, setup):
    with session_factory() as s:
        s.add(Faq(keywords="登录,密码", question="登录失败怎么办", answer="请重置密码"))
        s.commit()
    assert run(MatchFaqTool(), ctx, question="登录失败怎么办") == "请重置密码"


def test_match_faq_miss(session_factory, store, ctx, setup):
    assert run(MatchFaqTool(), ctx, question="今天天气如何") == "NO_MATCH"


def test_set_get_preference(session_factory, store, ctx, setup):
    run(SetPreferenceTool(), ctx, key="nickname", value="小王")
    assert run(GetPreferenceTool(), ctx, key="nickname") == "小王"


def test_record_question(session_factory, store, ctx, setup):
    run(RecordQuestionTool(), ctx, question="怎么改密码", resolution="faq_hit")
    with session_factory() as s:
        r = s.query(QuestionRecord).one()
        assert r.user_id == "u1"
        assert r.resolution == "faq_hit"


def test_record_feedback(session_factory, store, ctx, setup):
    run(RecordFeedbackTool(), ctx, rating="5")
    with session_factory() as s:
        f = s.query(Feedback).one()
        assert f.user_id == "u1"
        assert f.rating == "5"


def test_entry_points_registered():
    names = {ep.name for ep in entry_points(group="nanobot.tools")}
    assert {
        "match_faq",
        "record_question",
        "get_user_preference",
        "set_user_preference",
        "record_feedback",
    } <= names
