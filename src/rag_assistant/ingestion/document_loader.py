from pathlib import Path

from rag_assistant.ingestion.chunker import (
    chunk_text,
)

DOCUMENTS_PATH = Path(__file__).resolve().parents[1] / "data" / "documents"

LIVE_METRICS_DOCUMENT = "NorthStar Live Platform Metrics"


def load_document_chunks(documents_path: Path = DOCUMENTS_PATH):
    """
    Chunk the static knowledge-base documents. These are indexed once in
    the vector store; live metrics are handled separately.
    """

    chunks = []

    for file_path in sorted(documents_path.glob("*.txt")):

        with open(
            file_path,
            encoding="utf-8",
        ) as file:

            content = file.read()

        document_chunks = chunk_text(content)

        for index, chunk in enumerate(document_chunks):

            chunks.append(
                {
                    "document": file_path.name,
                    "chunk_index": index,
                    "content": chunk,
                }
            )

    return chunks


def load_live_metrics_chunk():
    """
    Current platform KPIs as a single chunk, refreshed on every question.
    """

    from rag_assistant.data.platform_context import (
        get_platform_context,
    )

    return {
        "document": LIVE_METRICS_DOCUMENT,
        "chunk_index": 0,
        "content": get_platform_context(),
    }


def load_documents():

    return load_document_chunks() + [load_live_metrics_chunk()]
