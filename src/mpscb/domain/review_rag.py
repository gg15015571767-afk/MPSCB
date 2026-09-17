"""评论 RAG：向量化评论语料，检索与问题最相关的评论（Phase 2 完整 RAG）。

用 embedding 把评论编码成向量存盘，检索时做余弦相似度 top-k，作为 LLM 回答的上下文。
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from mpscb.domain.rag import embed


def build_index(reviews: list[dict], out_dir: str | Path) -> int:
    """把评论列表（每项含 text 等字段）向量化并存盘，返回条数。"""
    texts = [r.get("text", "") for r in reviews]
    embs = np.asarray(embed(texts), dtype=np.float32)  # (N, 384) 已归一化
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "review_embeddings.npy", embs)
    (out / "review_texts.json").write_text(json.dumps(reviews, ensure_ascii=False), encoding="utf-8")
    return len(texts)


def retrieve(query: str, index_dir: str | Path, top_k: int = 5) -> list[dict]:
    """检索与 query 语义最相似的 top_k 条评论（带相似度分数）。"""
    index_dir = Path(index_dir)
    embs = np.load(index_dir / "review_embeddings.npy")
    reviews = json.loads((index_dir / "review_texts.json").read_text(encoding="utf-8"))
    q = np.asarray(embed([query])[0], dtype=np.float32)
    sims = embs @ q  # 已归一化，点积即余弦
    top_idx = np.argsort(-sims)[:top_k]
    return [{**reviews[int(i)], "score": float(sims[int(i)])} for i in top_idx]


def load_reviews(csv_path: str | Path) -> list[dict]:
    """从 CSV 加载评论（含 text/title/rating/department 字段）。"""
    import csv

    rows = list(csv.DictReader(Path(csv_path).open(encoding="utf-8-sig")))
    return [
        {
            "text": r["Review Text"].strip(),
            "title": r["Title"].strip(),
            "rating": r["Rating"],
            "department": r["Department Name"],
        }
        for r in rows
        if r["Review Text"].strip()
    ]


def ensure_index(csv_path: str | Path, index_dir: str | Path) -> bool:
    """若索引不存在则从 CSV 构建（约 1 分钟）；返回是否构建了。"""
    index_dir = Path(index_dir)
    if (index_dir / "review_embeddings.npy").exists():
        return False
    csv_path = Path(csv_path)
    if not csv_path.exists():
        return False
    build_index(load_reviews(csv_path), index_dir)
    return True


def ensure_qa_index(csv_path: str | Path, index_dir: str | Path) -> bool:
    """若电信问答索引不存在则从 CSV 构建（约 1-2 分钟）；返回是否构建了。"""
    index_dir = Path(index_dir)
    if (index_dir / "review_embeddings.npy").exists():
        return False
    csv_path = Path(csv_path)
    if not csv_path.exists():
        return False
    build_index(load_telecom_qa(csv_path), index_dir)
    return True


def load_telecom_qa(csv_path: str | Path, limit: int | None = None) -> list[dict]:
    """加载电信问答数据，返回 [{"text": 问题, "answer": 最佳回答}]，只取 is_best=1。

    question 字段为空时回退用 title（短版问题）。
    """
    import csv

    qa: list[dict] = []
    with open(csv_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("is_best") != "1":
                continue
            q = (r.get("question") or "").strip() or (r.get("title") or "").strip()
            a = (r.get("reply") or "").strip()
            if q and a:
                qa.append({"text": q, "answer": a})
            if limit is not None and len(qa) >= limit:
                break
    return qa
