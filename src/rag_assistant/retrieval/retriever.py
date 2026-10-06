from rag_assistant.ingestion.document_loader import (
    load_document_chunks,
)
from rag_assistant.vectorstore.qdrant_store import (
    KnowledgeIndex,
    make_client,
)

_index: KnowledgeIndex | None = None


def get_index() -> KnowledgeIndex:
    """
    Process-wide knowledge index. Embedded Qdrant locks its directory, so
    one client per process is required, not just cheaper.
    """

    global _index

    if _index is None:

        _index = KnowledgeIndex(
            load_document_chunks(),
            make_client(),
        )

    return _index


def retrieve_documents(
    query,
    top_k=3,
    index: KnowledgeIndex | None = None,
):

    return (index or get_index()).search(
        query,
        top_k=top_k,
    )
