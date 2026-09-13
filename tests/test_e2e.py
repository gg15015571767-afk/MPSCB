"""E2E 串联测试：工具 + MCP + 领域 + 数据共享同一 session_factory，走完整客服闭环。

不依赖真实 LLM / 飞书（那些需要凭证），验证的是各层代码确实串起来了。
"""

from __future__ import annotations

import asyncio
import re

from nanobot.agent.tools.context import RequestContext, request_context

from mpscb.app import init_runtime
from mpscb.domain.models import Faq, Feedback, QuestionRecord, Ticket
from mpscb.mcp_server.server import build_mcp
from mpscb.tools import state
from mpscb.tools.faq_tool import MatchFaqTool
from mpscb.tools.feedback_tool import RecordFeedbackTool
from mpscb.tools.question_tool import RecordQuestionTool


def _text(result) -> str:
    if isinstance(result, tuple):
        result = result[0]
    if isinstance(result, dict):
        return result.get("text") or result.get("result") or str(result)
    return "\n".join(getattr(b, "text", "") for b in result if getattr(b, "text", None))


def test_e2e_full_flow(tmp_path):
    init_runtime(db_path=str(tmp_path / "e2e.db"), pref_path=str(tmp_path / "pref.json"))
    session_factory = state.get_session_factory()

    with session_factory() as s:
        s.add(Faq(keywords="退款", question="如何退款", answer="7 天内可退"))
        s.commit()

    ctx = RequestContext(
        channel="feishu", chat_id="c1", sender_id="u1", session_key="feishu:c1"
    )
    mcp = build_mcp(session_factory)

    async def flow():
        with request_context(ctx):
            # 1) FAQ 命中
            assert await MatchFaqTool().execute(question="如何退款") == "7 天内可退"
            # 2) 问题记录留痕
            await RecordQuestionTool().execute(question="如何退款", resolution="faq_hit")
            # 3) 转人工：MCP 建单 + 标待人工
            created = _text(
                await mcp.call_tool(
                    "create_ticket",
                    {"title": "复杂问题", "description": "需人工", "user_id": "u1"},
                )
            )
            ticket_no = re.search(r"TK-\d{8}-\d{4}", created).group()
            await mcp.call_tool(
                "update_ticket_status", {"ticket_no": ticket_no, "status": "waiting_human"}
            )
            # 4) 满意度反馈
            await RecordFeedbackTool().execute(rating="satisfied")

    asyncio.run(flow())

    # 验证四张表在同一 DB 内一致
    with session_factory() as s:
        assert s.query(Faq).count() == 1
        assert s.query(QuestionRecord).count() == 1
        assert s.query(Ticket).count() == 1
        assert s.query(Ticket).one().status == "waiting_human"
        assert s.query(Feedback).count() == 1
        assert s.query(Feedback).one().rating == "satisfied"
