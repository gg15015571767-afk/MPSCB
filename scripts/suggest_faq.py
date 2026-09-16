"""反馈闭环：分析高频未命中问题，建议补进 FAQ（Step 3 自学习）。

用法：python scripts/suggest_faq.py
"""

from __future__ import annotations

import os

from mpscb.domain import stats as stats_service
from mpscb.domain.db import create_engine_for_db, make_session_factory

DEFAULT_DB = "data/mpscb.db"


def main() -> None:
    sf = make_session_factory(create_engine_for_db(os.environ.get("MPSCB_DB", DEFAULT_DB)))
    with sf() as s:
        unanswered = stats_service.unanswered_questions(s)

    if not unanswered:
        print("（暂无未命中问题，知识库覆盖良好）")
        return

    print("=" * 50)
    print("  建议补进 FAQ 的高频未命中问题")
    print("=" * 50)
    for i, (q, cnt) in enumerate(unanswered, 1):
        print(f"  {i:2d}. [{cnt} 次] {q}")
    print("\n这些是用户常问、但 FAQ 没覆盖的问题，可用 `python scripts/faq_cli.py add` 补进知识库。")


if __name__ == "__main__":
    main()
