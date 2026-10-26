"""
Azure AI Search backend for the NorthStar knowledge base.

Same interface as qdrant_store.KnowledgeIndex (search / upsert / count /
collection), so the assistant and the evals can run on either. Select it
with RAG_BACKEND=azure_search plus AZURE_SEARCH_ENDPOINT and
AZURE_SEARCH_KEY; infra/search.bicep creates the service.

Chunks are embedded locally with the same model as the Qdrant index
(all-MiniLM-L6-v2, title-prefixed) and pushed as vectors, so the two
backends differ only in the search engine, which is what the comparison
measures. Retrieval modes:

    dense      vector search (HNSW, cosine)
    hybrid     BM25 + vector, fused by Azure's reciprocal rank fusion
    semantic   hybrid, then Azure's semantic ranker
    rerank=True (any mode): the local cross-encoder reorders candidates

As in the Qdrant backend, every result's "score" is its cosine similarity
to the query, computed from the stored vector, so the relevance gate's
threshold means the same thing on both backends.
"""

from __future__ import annotations

import os

import numpy as np

from rag_assistant.embeddings.embedding_generator import (
    generate_embeddings,
    model as embedding_model,
)
from rag_assistant.retrieval.reranker import rerank as rerank_results
from rag_assistant.vectorstore.qdrant_store import (
    CANDIDATES,
    MODE_DENSE,
    MODE_HYBRID,
    embedding_text,
    fingerprint,
    point_id,
)

MODE_SEMANTIC = "semantic"

INDEX_PREFIX = "northstar-kb-"

SEMANTIC_CONFIG = "northstar-semantic"

# Production defaults on this backend, chosen from run_evals.py --compare --backend azure_search
# (2026-10-26): hybrid + Azure's semantic ranker matched hybrid + the local cross-encoder on every
# quality metric (keyword hit@1 100%, MRR 1.000) at ~40% lower latency, with no local model.
DEFAULT_MODE = MODE_SEMANTIC

DEFAULT_RERANK = False


def _clients(endpoint: str, key: str, index_name: str):

    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient

    credential = AzureKeyCredential(key)

    return (
        SearchIndexClient(endpoint, credential),
        SearchClient(endpoint, index_name, credential),
    )


def _index_definition(name: str, dimension: int):

    from azure.search.documents.indexes.models import (
        HnswAlgorithmConfiguration,
        SearchableField,
        SearchField,
        SearchFieldDataType,
        SearchIndex,
        SemanticConfiguration,
        SemanticField,
        SemanticPrioritizedFields,
        SemanticSearch,
        SimpleField,
        VectorSearch,
        VectorSearchAlgorithmMetric,
        VectorSearchProfile,
    )

    return SearchIndex(
        name=name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="document", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="chunk_index", type=SearchFieldDataType.Int32),
            SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                retrievable=True,
                vector_search_dimensions=dimension,
                vector_search_profile_name="hnsw-cosine",
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hnsw", parameters={"metric": VectorSearchAlgorithmMetric.COSINE}
                )
            ],
            profiles=[VectorSearchProfile(name="hnsw-cosine", algorithm_configuration_name="hnsw")],
        ),
        semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name=SEMANTIC_CONFIG,
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                    ),
                )
            ]
        ),
    )


class AzureSearchIndex:
    """
    The knowledge base as an Azure AI Search index.
    """

    backend = "azure_search"

    default_mode = DEFAULT_MODE

    default_rerank = DEFAULT_RERANK

    def __init__(self, chunks: list[dict], endpoint: str | None = None, key: str | None = None) -> None:

        endpoint = endpoint or os.environ["AZURE_SEARCH_ENDPOINT"]
        key = key or os.environ["AZURE_SEARCH_KEY"]

        # The index name carries the content fingerprint, as in the Qdrant
        # backend: edited documents rebuild, unchanged ones are reused.
        self.collection = INDEX_PREFIX + fingerprint(chunks)
        self.dimension = embedding_model.get_embedding_dimension()
        self.index_client, self.client = _clients(endpoint, key, self.collection)

        existing = set(self.index_client.list_index_names())

        if self.collection not in existing:
            # The Free tier allows only 3 indexes: drop stale versions first.
            for name in existing:
                if name.startswith(INDEX_PREFIX):
                    self.index_client.delete_index(name)
            self.index_client.create_index(_index_definition(self.collection, self.dimension))
            self.upsert(chunks)
            self._wait_until_searchable(len(chunks))

    def _wait_until_searchable(self, expected: int, timeout_s: float = 60.0) -> None:
        """Uploads are indexed asynchronously; don't let the first queries race them."""

        import time

        deadline = time.monotonic() + timeout_s
        while self.count() < expected and time.monotonic() < deadline:
            time.sleep(1)

    def upsert(self, chunks: list[dict]) -> None:

        if not chunks:
            return

        texts = [embedding_text(c) for c in chunks]

        self.client.merge_or_upload_documents(
            [
                {
                    "id": point_id(c["document"], c["chunk_index"]),
                    "document": c["document"],
                    "chunk_index": int(c["chunk_index"]),
                    "title": text.split(":", 1)[0],
                    "content": c["content"],
                    "embedding": [float(v) for v in vector],
                }
                for c, text, vector in zip(chunks, texts, generate_embeddings(texts))
            ]
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
        mode: str | None = None,
        rerank: bool | None = None,
    ) -> list[dict]:

        from azure.search.documents.models import VectorizedQuery

        mode = mode or DEFAULT_MODE
        rerank = DEFAULT_RERANK if rerank is None else rerank

        dense_query = np.asarray(generate_embeddings([query])[0], dtype=float)
        dense_query /= np.linalg.norm(dense_query) or 1.0

        limit = CANDIDATES if rerank else top_k
        vector = VectorizedQuery(vector=dense_query.tolist(), k_nearest_neighbors=CANDIDATES, fields="embedding")

        if mode == MODE_DENSE:
            request = dict(search_text=None, vector_queries=[vector])
        elif mode == MODE_HYBRID:
            request = dict(search_text=query, vector_queries=[vector])
        elif mode == MODE_SEMANTIC:
            request = dict(
                search_text=query,
                vector_queries=[vector],
                query_type="semantic",
                semantic_configuration_name=SEMANTIC_CONFIG,
            )
        else:
            raise ValueError(f"unknown retrieval mode: {mode}")

        hits = list(
            self.client.search(top=limit, select=["document", "content", "embedding"], **request)
        )

        results = []

        for hit in hits:

            stored = np.asarray(hit["embedding"], dtype=float)
            stored /= np.linalg.norm(stored) or 1.0

            results.append(
                {
                    "document": hit["document"],
                    "content": hit["content"],
                    "score": round(float(np.dot(dense_query, stored)), 3),
                }
            )

        if rerank:
            return rerank_results(query, results, top_k)

        return results[:top_k]

    def count(self) -> int:

        return self.client.get_document_count()
