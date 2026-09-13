"""工单 MCP Server 测试（通过 call_tool 调用，不真正起 stdio 进程）。"""

from __future__ import annotations

import asyncio
import re

from mpscb.mcp_server.server import build_mcp


def _text(result) -> str:
    # call_tool 返回 (content_blocks, structured_metadata) 或 dict
    if isinstance(result, tuple):
        result = result[0]
    if isinstance(result, dict):
        return result.get("text") or result.get("result") or str(result)
    return "\n".join(
        getattr(b, "text", "") for b in result if getattr(b, "text", None) is not None
    )


def _call(mcp, name, **args) -> str:
    return _text(asyncio.run(mcp.call_tool(name, args)))


def test_create_query_update(session_factory):
    mcp = build_mcp(session_factory)
    out = _call(
        mcp,
        "create_ticket",
        title="无法登录",
        description="登录失败",
        user_id="u1",
    )
    assert "工单已创建" in out
    no = re.search(r"TK-\d{8}-\d{4}", out).group()

    assert "pending" in _call(mcp, "query_ticket", ticket_no=no)

    out3 = _call(mcp, "update_ticket_status", ticket_no=no, status="waiting_human")
    assert "waiting_human" in out3
    assert "waiting_human" in _call(mcp, "query_ticket", ticket_no=no)


def test_query_missing(session_factory):
    mcp = build_mcp(session_factory)
    assert "未找到工单" in _call(mcp, "query_ticket", ticket_no="TK-NOPE")


def test_update_invalid_status(session_factory):
    mcp = build_mcp(session_factory)
    no = re.search(
        r"TK-\d{8}-\d{4}",
        _call(mcp, "create_ticket", title="a", description="d", user_id="u1"),
    ).group()
    out = _call(mcp, "update_ticket_status", ticket_no=no, status="bogus")
    assert "非法工单状态" in out
