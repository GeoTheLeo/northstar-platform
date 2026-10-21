"""
Hybrid (dense + BM25) retrieval and cross-encoder reranking.
"""

from rag_assistant.chat.answer_generator import (
    MIN_RELEVANCE,
    STATUS_LOW_RELEVANCE,
    answer_question,
    top_score,
)
from rag_assistant.evals.run_evals import evaluate_retrieval, load_golden_set
from rag_assistant.vectorstore import sparse
from rag_assistant.vectorstore.qdrant_store import (
    MODE_DENSE,
    MODE_HYBRID,
    KnowledgeIndex,
    fingerprint,
    make_client,
)


def test_tokenizer_drops_stopwords_and_folds_plurals():

    assert sparse.tokenize("What are the Segments of the 80/20 split?") == ["segment", "80", "20", "split"]


def test_repeated_terms_weigh_more_and_ids_are_stable():

    vector = sparse.document_vector("KMeans KMeans clustering")
    weights = dict(zip(vector.indices, vector.values))

    assert weights[sparse._term_id("kmean")] > weights[sparse._term_id("clustering")]
    # CRC32, not Python's per-process salted hash(): ids must survive a restart.
    assert sparse._term_id("kmean") == 2038202861


def test_keyword_match_beats_a_closer_embedding():
    """
    "Platform Healthy" names a rule in the advisor document, but its embedding
    sits closer to the platform overview. Hybrid + rerank puts the rule first.
    """

    client = make_client(":memory:")
    index = KnowledgeIndex(
        [
            {"document": "overview.txt", "chunk_index": 0,
             "content": "NorthStar is a platform for learner success with a healthy set of modules."},
            {"document": "rules.txt", "chunk_index": 0,
             "content": "If none of these rules fire, the advisor reports Platform Healthy and continues monitoring."},
        ],
        client,
    )

    [best] = index.search("Platform Healthy", top_k=1, mode=MODE_HYBRID, rerank=True)

    assert best["document"] == "rules.txt"


def test_score_is_cosine_similarity_in_every_mode(knowledge_index):

    query = "How many trees are in the at-risk classifier?"

    dense = {(r["document"], r["content"]): r["score"] for r in knowledge_index.search(query, top_k=5, mode=MODE_DENSE, rerank=False)}
    hybrid = knowledge_index.search(query, top_k=5, mode=MODE_HYBRID, rerank=True)

    shared = [r for r in hybrid if (r["document"], r["content"]) in dense]

    assert shared
    for r in shared:
        assert abs(r["score"] - dense[(r["document"], r["content"])]) < 0.002
        assert "rerank_score" in r


def test_relevance_gate_uses_the_best_score_not_the_first():
    """
    After reranking, the first chunk can be less similar than a later one;
    the gate must not refuse just because of the order.
    """

    reranked = [
        {"document": "a.txt", "content": "A", "score": MIN_RELEVANCE - 0.1},
        {"document": "b.txt", "content": "B", "score": MIN_RELEVANCE + 0.2},
    ]

    assert top_score(reranked) == MIN_RELEVANCE + 0.2
    assert top_score([]) is None

    gated = answer_question("q", [dict(reranked[0])])

    assert gated.status == STATUS_LOW_RELEVANCE


def test_schema_version_is_part_of_the_fingerprint(monkeypatch):

    chunks = [{"document": "a.txt", "chunk_index": 0, "content": "Same."}]

    current = fingerprint(chunks)

    monkeypatch.setattr("rag_assistant.vectorstore.qdrant_store.SCHEMA_VERSION", 1)

    assert fingerprint(chunks) != current


def test_keyword_queries_regression_gate(knowledge_index):
    """
    The production configuration (hybrid + rerank) must find every
    keyword-style query's document first, and beat dense-only on them.
    """

    golden = load_golden_set()

    production = evaluate_retrieval(knowledge_index, golden)
    dense = evaluate_retrieval(knowledge_index, golden, mode=MODE_DENSE, rerank=False)

    assert production["keyword_hit_at_1"] == 1.0
    assert production["keyword_mrr"] > dense["keyword_mrr"]
    assert production["off_topic_gated"] == 1.0
