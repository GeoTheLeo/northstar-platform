"""
Azure AI Search backend.

The index-definition test runs offline. The retrieval regression runs only
when AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY are set (it talks to the real
service), so CI without Azure credentials skips it.
"""

import os

import pytest

pytest.importorskip("azure.search.documents")

from rag_assistant.evals.run_evals import AZURE_CONFIGS, evaluate_retrieval, load_golden_set  # noqa: E402
from rag_assistant.ingestion.document_loader import load_document_chunks  # noqa: E402
from rag_assistant.vectorstore import azure_search_store  # noqa: E402

LIVE = bool(os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_SEARCH_KEY"))


def test_index_has_text_vector_and_semantic_config():

    index = azure_search_store._index_definition("northstar-kb-test", 384)
    fields = {f.name: f for f in index.fields}

    assert fields["id"].key
    assert fields["embedding"].vector_search_dimensions == 384
    assert fields["embedding"].vector_search_profile_name == "hnsw-cosine"
    assert {"title", "content"} <= set(fields)
    assert index.semantic_search.configurations[0].name == azure_search_store.SEMANTIC_CONFIG


@pytest.mark.skipif(not LIVE, reason="needs AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY")
def test_golden_set_on_azure_ai_search():
    """
    The production configuration on Azure (hybrid + semantic ranker) must
    find every keyword query's document first, keep every answerable question
    in the top 3, and still gate every off-topic question.
    """

    index = azure_search_store.AzureSearchIndex(load_document_chunks())
    mode, rerank = AZURE_CONFIGS["hybrid + semantic ranker"]

    report = evaluate_retrieval(index, load_golden_set(), mode=mode, rerank=rerank)

    assert report["hit_at_3"] == 1.0
    assert report["keyword_hit_at_1"] == 1.0
    assert report["answerable_above_threshold"] == 1.0
    assert report["off_topic_gated"] == 1.0
