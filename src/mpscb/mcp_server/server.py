"""工单 MCP Server（stdio）。

暴露 create_ticket / query_ticket / update_ticket_status，让 Agent 具备工单能力。
由 nanobot 的 mcp_servers 配置以 stdio 子进程启动；DB 路径经环境变量 MPSCB_DB 传入。
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from mpscb.domain.db import create_engine_for_db, make_session_factory
from mpscb.domain.ticket import (
    create_ticket as _create_ticket,
    get_ticket as _get_ticket,
    update_status as _update_status,
)

DEFAULT_DB = "data/mpscb.db"


def build_mcp(session_factory) -> FastMCP:
    """构造 MCP 服务器（注入 session_factory，便于测试）。"""
    mcp = FastMCP("mpscb-ticket")

    @mcp.tool()
    def create_ticket(
        title: str,
        description: str,
        user_id: str,
        channel: str = "feishu",
        session_id: str | None = None,
    ) -> str:
        with session_factory() as s:
            t = _create_ticket(
                s,
                title=title,
                description=description,
                user_id=user_id,
                channel=channel,
                session_id=session_id,
            )
        return f"工单已创建，工单号：{t.ticket_no}"

    @mcp.tool()
    def query_ticket(ticket_no: str) -> str:
        with session_factory() as s:
            t = _get_ticket(s, ticket_no)
        return f"工单 {ticket_no} 状态：{t.status}" if t else f"未找到工单 {ticket_no}"

    @mcp.tool()
    def update_ticket_status(ticket_no: str, status: str) -> str:
        with session_factory() as s:
            try:
                t = _update_status(s, ticket_no, status)
            except ValueError as e:
                return str(e)
        return (
            f"工单 {ticket_no} 状态已更新为 {status}" if t else f"未找到工单 {ticket_no}"
        )

    return mcp


def main() -> None:
    db = os.environ.get("MPSCB_DB", DEFAULT_DB)
    engine = create_engine_for_db(db)
    session_factory = make_session_factory(engine)
    mcp = build_mcp(session_factory)
    mcp.run()  # 默认 stdio


if __name__ == "__main__":
    main()
