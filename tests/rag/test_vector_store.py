"""
Qdrant knowledge index, chunking, and retrieval quality on the golden set.
"""

from rag_assistant.evals.run_evals import evaluate_retrieval, load_golden_set
from rag_assistant.ingestion.chunker import chunk_text
from rag_assistant.ingestion.document_loader import load_document_chunks
from rag_assistant.vectorstore.qdrant_store import (
    COLLECTION_PREFIX,
    KnowledgeIndex,
    make_client,
)


def test_every_chunk_is_indexed(knowledge_index):

    assert knowledge_index.count() == len(load_document_chunks())


def test_unchanged_documents_reuse_the_collection():

    client = make_client(":memory:")
    chunks = [{"document": "a.txt", "chunk_index": 0, "content": "Alpha content."}]

    first = KnowledgeIndex(chunks, client)
    second = KnowledgeIndex(chunks, client)

    assert first.collection == second.collection
    assert second.count() == 1


def test_edited_documents_reindex_and_drop_the_stale_collection():

    client = make_client(":memory:")

    old = KnowledgeIndex([{"document": "a.txt", "chunk_index": 0, "content": "Old."}], client)
    new = KnowledgeIndex([{"document": "a.txt", "chunk_index": 0, "content": "New."}], client)

    names = [c.name for c in client.get_collections().collections if c.name.startswith(COLLECTION_PREFIX)]

    assert old.collection != new.collection
    assert names == [new.collection]


def test_upserting_the_same_chunk_overwrites_it():

    client = make_client(":memory:")
    index = KnowledgeIndex([{"document": "a.txt", "chunk_index": 0, "content": "Static."}], client)

    live = {"document": "live", "chunk_index": 0, "content": "Retention 80%."}

    index.upsert([live])
    index.upsert([dict(live, content="Retention 90%.")])

    assert index.count() == 2
    assert index.search("retention", top_k=1)[0]["content"] == "Retention 90%."


def test_chunker_keeps_rules_with_their_consequences():

    text = (
        "Intro line.\n\n"
        "If the intervention rate is above 10 percent, raise a recommendation. "
        "Expected time to impact is 3 to 6 weeks.\n\n"
        "If no rule fires, report Platform Healthy and continue monitoring as usual."
    )

    chunks = chunk_text(text)

    rule = next(c for c in chunks if "intervention rate" in c)

    assert "3 to 6 weeks" in rule
    assert chunks[0].startswith("Intro line.")


def test_golden_set_retrieval_quality(knowledge_index):
    """
    Regression gate: every answerable question retrieves its source document
    in the top 3 and clears the relevance gate; every off-topic one is gated.
    """

    report = evaluate_retrieval(knowledge_index, load_golden_set())

    assert report["hit_at_3"] == 1.0
    assert report["hit_at_1"] >= 0.85
    assert report["answerable_above_threshold"] == 1.0
    assert report["off_topic_gated"] == 1.0
