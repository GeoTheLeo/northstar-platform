from pathlib import Path

from rag_assistant.data.platform_context import (
    get_platform_context,
)
from rag_assistant.ingestion.chunker import (
    chunk_text,
)

DOCUMENTS_PATH = Path("src/rag_assistant/data/documents")


def load_documents():

    chunks = []

    for file_path in DOCUMENTS_PATH.glob("*.txt"):

        with open(
            file_path,
            encoding="utf-8",
        ) as file:

            content = file.read()

        document_chunks = chunk_text(content)

        for chunk in document_chunks:

            chunks.append(
                {
                    "document": file_path.name,
                    "content": chunk,
                }
            )

    platform_context = get_platform_context()

    chunks.append(
        {
            "document": "NorthStar Live Platform Metrics",
            "content": platform_context,
        }
    )

    return chunks
