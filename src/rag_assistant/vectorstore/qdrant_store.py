"""
Qdrant vector store for the NorthStar knowledge base.

Runs embedded (local files, no server) by default. Set QDRANT_URL (and
QDRANT_API_KEY if needed) to use a Qdrant server or Qdrant Cloud instead;
nothing else changes.

Documents are embedded once. The collection name carries a fingerprint of
the document contents, so editing a document triggers a re-index and an
unchanged knowledge base is reused across restarts.
"""

import hashlib
import json
import os
import threading
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from rag_assistant.embeddings.embedding_generator import (
    generate_embeddings,
    model as embedding_model,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_PATH = PROJECT_ROOT / "data" / "vector_store"

COLLECTION_PREFIX = "northstar_kb_"

_POINT_NAMESPACE = uuid.UUID("6f1c2a52-6a3c-4c8e-9a51-1f0b7a6d2c11")


def fingerprint(chunks: list[dict]) -> str:
    """
    Stable hash of the chunk set, used to version the collection.
    """

    payload = json.dumps(
        [[c["document"], c["chunk_index"], c["content"]] for c in chunks],
        sort_keys=True,
    )

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def embedding_text(chunk: dict) -> str:
    """
    Text that gets embedded: the chunk prefixed with its document title.
    A paragraph like "The model is a Random Forest..." never names the
    early warning system itself; the title header supplies that context.
    """

    title = Path(chunk["document"]).stem.replace("_", " ")

    return f"{title}: {chunk['content']}"


def point_id(document: str, chunk_index: int) -> str:

    return str(uuid.uuid5(_POINT_NAMESPACE, f"{document}#{chunk_index}"))


def make_client(location: str | None = None) -> QdrantClient:
    """
    location=":memory:" for tests; otherwise QDRANT_URL or the local path.
    """

    if location is not None:
        return QdrantClient(location=location)

    url = os.getenv("QDRANT_URL")

    if url:
        return QdrantClient(url=url, api_key=os.getenv("QDRANT_API_KEY"))

    DEFAULT_PATH.mkdir(parents=True, exist_ok=True)

    return QdrantClient(path=str(DEFAULT_PATH))


class KnowledgeIndex:
    """
    The knowledge base as a Qdrant collection.
    """

    def __init__(self, chunks: list[dict], client: QdrantClient) -> None:

        self.client = client

        # Streamlit serves each session on its own thread; serialise access
        # to the shared client (embedded Qdrant is not thread-safe).
        self._lock = threading.Lock()

        self.collection = COLLECTION_PREFIX + fingerprint(chunks)

        self.dimension = embedding_model.get_embedding_dimension()

        if not self.client.collection_exists(self.collection):
            self._build(chunks)

        self._drop_stale_collections()

    def _build(self, chunks: list[dict]) -> None:

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
        )

        self.upsert(chunks)

    def _drop_stale_collections(self) -> None:

        for existing in self.client.get_collections().collections:

            if (
                existing.name.startswith(COLLECTION_PREFIX)
                and existing.name != self.collection
            ):
                self.client.delete_collection(existing.name)

    def upsert(self, chunks: list[dict]) -> None:
        """
        Insert or replace chunks. Point IDs derive from document and chunk
        index, so re-upserting a chunk (e.g. live metrics) overwrites it.
        """

        if not chunks:
            return

        vectors = generate_embeddings([embedding_text(c) for c in chunks])

        with self._lock:
            self._upsert(chunks, vectors)

    def _upsert(self, chunks: list[dict], vectors) -> None:

        self.client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=point_id(c["document"], c["chunk_index"]),
                    vector=[float(v) for v in vector],
                    payload=c,
                )
                for c, vector in zip(chunks, vectors)
            ],
        )

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Top-k chunks by cosine similarity, highest first.
        """

        query_vector = [float(v) for v in generate_embeddings([query])[0]]

        with self._lock:
            hits = self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                limit=top_k,
                with_payload=True,
            ).points

        return [
            {
                "document": hit.payload["document"],
                "content": hit.payload["content"],
                "score": round(float(hit.score), 3),
            }
            for hit in hits
        ]

    def count(self) -> int:

        return self.client.count(self.collection).count
