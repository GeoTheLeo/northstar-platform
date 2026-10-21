"""
Cross-encoder reranking.

The bi-encoder used for embeddings scores the query and each chunk
separately; a cross-encoder reads them together, which is slower but
better at telling the best match from a close second. It only ever sees a
short candidate list, so it adds well under 0.1 s per question on CPU.

Loaded on first use (about 90 MB, cached by Hugging Face after the first
download), so importing this module costs nothing.
"""

import threading

RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"

_model = None

_lock = threading.Lock()


def _get_model():

    global _model

    with _lock:

        if _model is None:

            from sentence_transformers import CrossEncoder

            _model = CrossEncoder(RERANK_MODEL)

    return _model


def rerank(query: str, results: list[dict], top_k: int) -> list[dict]:
    """
    Reorder results by cross-encoder relevance and keep the top_k. Each
    result gains a "rerank_score"; its "score" (cosine similarity, used by
    the relevance gate) is left unchanged.
    """

    if not results:
        return []

    scores = _get_model().predict([(query, r["content"]) for r in results])

    ranked = sorted(
        (dict(r, rerank_score=round(float(s), 3)) for r, s in zip(results, scores)),
        key=lambda r: r["rerank_score"],
        reverse=True,
    )

    return ranked[:top_k]
