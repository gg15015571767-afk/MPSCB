"""工单管理 CLI（人工侧闭环）。

用法（从项目根目录）：
  python scripts/ticket_cli.py stats
  python scripts/ticket_cli.py list [--status waiting_human]
  python scripts/ticket_cli.py show --no TK-xxxx
  python scripts/ticket_cli.py update --no TK-xxxx --status processing
"""

from __future__ import annotations

import argparse
import os

from mpscb.domain import ticket as ticket_service
from mpscb.domain.db import create_engine_for_db, make_session_factory
from mpscb.domain.models import TICKET_STATUSES

DEFAULT_DB = "data/mpscb.db"


def _engine_and_factory():
    db = os.environ.get("MPSCB_DB", DEFAULT_DB)
    return make_session_factory(create_engine_for_db(db))


def _fmt(t) -> str:
    return (
        f"[{t.ticket_no}] ({t.status}) {t.title}  |  "
        f"{t.user_id}@{t.channel}  |  {t.created_at.strftime('%m-%d %H:%M')}"
    )


def cmd_stats(args) -> None:
    sf = _engine_and_factory()
    with sf() as s:
        counts = ticket_service.count_tickets_by_status(s)
    if not counts:
        print("（暂无工单）")
        return
    for status in TICKET_STATUSES:
        print(f"  {status:14s} : {counts.get(status, 0)}")


def cmd_list(args) -> None:
    sf = _engine_and_factory()
    with sf() as s:
        tickets = ticket_service.list_all_tickets(s, args.status)
    if not tickets:
        print("（无工单）")
        return
    for t in tickets:
        print(_fmt(t))


def cmd_show(args) -> None:
    sf = _engine_and_factory()
    with sf() as s:
        t = ticket_service.get_ticket(s, args.no)
    if t is None:
        print(f"未找到工单 {args.no}")
        return
    print(f"工单号   : {t.ticket_no}")
    print(f"标题     : {t.title}")
    print(f"描述     : {t.description}")
    print(f"状态     : {t.status}")
    print(f"用户     : {t.user_id} @ {t.channel}")
    print(f"会话     : {t.session_id or '-'}")
    print(f"创建时间 : {t.created_at}")
    print(f"更新时间 : {t.updated_at}")


def cmd_update(args) -> None:
    sf = _engine_and_factory()
    with sf() as s:
        t = ticket_service.update_status(s, args.no, args.status)
    if t is None:
        print(f"未找到工单 {args.no}")
    else:
        print(f"工单 {t.ticket_no} 状态已更新为 {t.status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="工单管理")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("stats", help="各状态工单数量")

    p_list = sub.add_parser("list", help="列出工单")
    p_list.add_argument("--status", choices=TICKET_STATUSES, help="按状态过滤")

    p_show = sub.add_parser("show", help="查看工单详情")
    p_show.add_argument("--no", required=True, help="工单号")

    p_update = sub.add_parser("update", help="更新工单状态")
    p_update.add_argument("--no", required=True, help="工单号")
    p_update.add_argument(
        "--status", choices=TICKET_STATUSES, required=True, help="新状态"
    )

    args = parser.parse_args()
    {
        "stats": cmd_stats,
        "list": cmd_list,
        "show": cmd_show,
        "update": cmd_update,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
