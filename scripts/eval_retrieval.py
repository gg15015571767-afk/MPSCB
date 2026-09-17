"""RAG 检索质量评估（电信问答）。

做法：加载 ~9 万条「问题→最佳回答」→ 建向量索引 → 抽 1000 条测试 →
对每条检索 top-2（top-1 是自身，跳过）→ 统计「最相似的其他问题」的相似度。
相似度越高，说明 embedding 能把同类问题聚在一起（检索质量越好）。
"""

from __future__ import annotations

import random

from mpscb.domain.review_rag import build_index, load_telecom_qa, retrieve

CSV_PATH = "resources/anhuidianxinzhidao_filter.csv"
INDEX_DIR = "data/qa_index"


def main() -> None:
    qa = load_telecom_qa(CSV_PATH)
    print(f"加载 {len(qa)} 条问答，构建索引...")
    build_index(qa, INDEX_DIR)

    random.seed(42)
    test = random.sample(qa, 1000)

    sims = []
    for d in test:
        rs = retrieve(d["text"], INDEX_DIR, top_k=2)
        sim = rs[1]["score"] if len(rs) > 1 else 0.0
        sims.append(sim)

    avg = sum(sims) / len(sims)
    print("\n=== 检索质量评估（1000 条测试）===")
    print(f"平均 top-1（排除自身）相似度: {avg:.3f}")
    print(f"相似度 > 0.7 的比例: {sum(1 for s in sims if s > 0.7) / len(sims) * 100:.1f}%")
    print(f"相似度 > 0.8 的比例: {sum(1 for s in sims if s > 0.8) / len(sims) * 100:.1f}%")

    # 展示几个例子
    print("\n=== 检索示例 ===")
    for d in test[:3]:
        rs = retrieve(d["text"], INDEX_DIR, top_k=3)
        print(f"查询: {d['text'][:40]}")
        for r in rs[1:3]:  # 跳过自身
            print(f"  命中[{r['score']:.3f}]: {r['text'][:40]}")
        print()


if __name__ == "__main__":
    main()
