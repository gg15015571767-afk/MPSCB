"""RAG 语义检索：embedding 向量相似度匹配（Step 2 核心亮点）。

用 sentence-transformers + all-MiniLM-L6-v2（英文小模型，384 维）把问题与
候选 FAQ 问题编码成向量，用余弦相似度做语义匹配——命中关键词匹配不到的同义问法。
"""

from __future__ import annotations

import os
from functools import lru_cache


@lru_cache(maxsize=1)
def _get_model():
    # 国内环境走 HuggingFace 镜像，避免模型下载失败（可被已有 HF_ENDPOINT 覆盖）
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    from sentence_transformers import SentenceTransformer

    # 中文 embedding（可经 MPSCB_EMBED_MODEL 覆盖）
    return SentenceTransformer(os.environ.get("MPSCB_EMBED_MODEL", "BAAI/bge-small-zh-v1.5"))


def embed(texts: list[str]) -> list[list[float]]:
    """把文本列表编码成归一化向量（L2 归一化，便于点积当余弦）。"""
    if not texts:
        return []
    model = _get_model()
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()


def semantic_match(
    question: str,
    candidates: list[str],
    threshold: float = 0.45,
) -> tuple[int, float] | None:
    """返回与 question 语义最相似的 candidate 下标 + 余弦相似度；低于阈值返回 None。"""
    if not candidates:
        return None
    q_emb = embed([question])[0]
    best_idx, best_sim = -1, -1.0
    for i, cand_emb in enumerate(embed(candidates)):
        sim = float(sum(x * y for x, y in zip(q_emb, cand_emb)))  # 归一化后点积即余弦
        if sim > best_sim:
            best_idx, best_sim = i, sim
    if best_sim < threshold:
        return None
    return best_idx, best_sim
