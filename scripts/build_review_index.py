"""构建评论向量索引（一次性，约 1 分钟）。

用法：python scripts/build_review_index.py
输出：data/review_index/review_embeddings.npy + review_texts.json
"""

from __future__ import annotations

from mpscb.domain.review_rag import build_index, load_reviews

CSV_PATH = "resources/reviews.csv"
OUT_DIR = "data/review_index"


def main() -> None:
    reviews = load_reviews(CSV_PATH)
    n = build_index(reviews, OUT_DIR)
    print(f"已向量化 {n} 条评论 → {OUT_DIR}")


if __name__ == "__main__":
    main()
