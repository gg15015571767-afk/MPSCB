"""FAQ 知识库管理 CLI。

用法（从项目根目录）：
  python scripts/faq_cli.py list
  python scripts/faq_cli.py add --question "如何退款" --answer "7天内可退" --keywords "退款,退钱" --category "售后"
  python scripts/faq_cli.py import scripts/faq_seed.json
  python scripts/faq_cli.py delete --id 1
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from mpscb.domain import faq as faq_service
from mpscb.domain.db import create_engine_for_db, make_session_factory

DEFAULT_DB = "data/mpscb.db"


def _engine_and_factory():
    db = os.environ.get("MPSCB_DB", DEFAULT_DB)
    engine = create_engine_for_db(db)
    return make_session_factory(engine)


def cmd_list(args) -> None:
    sf = _engine_and_factory()
    with sf() as s:
        faqs = faq_service.list_faqs(s)
    if not faqs:
        print("（知识库为空）")
        return
    for f in faqs:
        print(f"[{f.id}] ({f.category or '-'}) {f.question} → {f.answer}   [关键词: {f.keywords}]")


def cmd_add(args) -> None:
    sf = _engine_and_factory()
    with sf() as s:
        f = faq_service.add_faq(
            s,
            question=args.question,
            answer=args.answer,
            keywords=args.keywords or "",
            category=args.category,
        )
    print(f"已添加 FAQ #{f.id}: {f.question}")


def cmd_import(args) -> None:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("faqs", [])
    sf = _engine_and_factory()
    with sf() as s:
        n = faq_service.import_faqs(s, items)
    print(f"已导入 {n} 条 FAQ（来自 {args.file}）")


def cmd_delete(args) -> None:
    sf = _engine_and_factory()
    with sf() as s:
        ok = faq_service.delete_faq(s, args.id)
    print(f"已删除 FAQ #{args.id}" if ok else f"未找到 FAQ #{args.id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="FAQ 知识库管理")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="列出所有 FAQ")

    p_add = sub.add_parser("add", help="添加一条 FAQ")
    p_add.add_argument("--question", required=True, help="标准问法")
    p_add.add_argument("--answer", required=True, help="标准答案")
    p_add.add_argument("--keywords", help="关键词，逗号分隔")
    p_add.add_argument("--category", help="分类（可选）")

    p_import = sub.add_parser("import", help="从 JSON 文件批量导入")
    p_import.add_argument("file", help="JSON 文件路径（列表或 {faqs: [...]}）")

    p_del = sub.add_parser("delete", help="按 id 删除一条 FAQ")
    p_del.add_argument("--id", type=int, required=True, help="FAQ id")

    args = parser.parse_args()
    {"list": cmd_list, "add": cmd_add, "import": cmd_import, "delete": cmd_delete}[
        args.cmd
    ](args)


if __name__ == "__main__":
    main()
