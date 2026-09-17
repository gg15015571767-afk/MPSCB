"""电信问答加载测试（mock CSV，测加载逻辑，不加载模型）。"""

from __future__ import annotations

import csv

from mpscb.domain.review_rag import load_telecom_qa


def _write(tmp_path):
    p = tmp_path / "t.csv"
    with open(p, "w", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["title", "question", "reply", "is_best"])
        w.writerow(["标题1", "完整问题1", "回答1", "1"])  # best
        w.writerow(["标题1", "完整问题1", "回答2", "0"])  # 非 best，应跳过
        w.writerow(["标题2", "", "回答3", "1"])  # question 空 → 回退 title
        w.writerow(["标题3", "", "", "1"])  # reply 空 → 跳过
    return p


def test_load_telecom_qa(tmp_path):
    qa = load_telecom_qa(str(_write(tmp_path)))
    assert len(qa) == 2  # 跳过非 best 和 reply 空
    assert qa[0]["text"] == "完整问题1"  # question 非空 → 用 question
    assert qa[0]["answer"] == "回答1"
    assert qa[1]["text"] == "标题2"  # question 空 → 回退 title


def test_load_telecom_qa_limit(tmp_path):
    qa = load_telecom_qa(str(_write(tmp_path)), limit=1)
    assert len(qa) == 1
