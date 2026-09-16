"""运营统计报表（运维观测）。

用法：python scripts/stats_cli.py
"""

from __future__ import annotations

import os

from mpscb.domain import stats as stats_service
from mpscb.domain import ticket as ticket_service
from mpscb.domain.db import create_engine_for_db, make_session_factory
from mpscb.domain.models import RESOLUTIONS, TICKET_STATUSES

DEFAULT_DB = "data/mpscb.db"


def _engine_and_factory():
    db = os.environ.get("MPSCB_DB", DEFAULT_DB)
    return make_session_factory(create_engine_for_db(db))


def main() -> None:
    sf = _engine_and_factory()
    with sf() as s:
        res = stats_service.count_questions_by_resolution(s)
        hit_rate = stats_service.faq_hit_rate(s)
        ratings = stats_service.count_feedbacks_by_rating(s)
        avg = stats_service.average_rating(s)
        tickets = ticket_service.count_tickets_by_status(s)

    total_q = sum(res.values())
    print("=" * 46)
    print("  运营统计")
    print("=" * 46)

    print("\n【FAQ 命中率】（问题处理路径）")
    if total_q == 0:
        print("  （暂无问题记录）")
    else:
        for r in RESOLUTIONS:
            cnt = res.get(r, 0)
            print(f"  {r:14s}: {cnt:5d}  ({cnt / total_q * 100:5.1f}%)")
        print(f"  {'合计':14s}: {total_q:5d}")
        if hit_rate is not None:
            print(f"  → FAQ 命中率: {hit_rate * 100:.1f}%")

    print("\n【满意度】（1-5 星）")
    if not ratings:
        print("  （暂无反馈）")
    else:
        for r in ("1", "2", "3", "4", "5"):
            print(f"  {r}★: {ratings.get(r, 0):5d}")
        if avg is not None:
            print(f"  → 平均分: {avg:.2f} / 5")

    print("\n【工单状态】")
    if not tickets:
        print("  （暂无工单）")
    else:
        for status in TICKET_STATUSES:
            print(f"  {status:14s}: {tickets.get(status, 0):5d}")
    print()


if __name__ == "__main__":
    main()
