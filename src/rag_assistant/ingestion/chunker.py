import re


def chunk_text(
    text,
    sentences_per_chunk=3,
):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    chunks = []

    current_chunk = []

    for sentence in sentences:

        current_chunk.append(sentence)

        if len(current_chunk) >= sentences_per_chunk:

            chunks.append(" ".join(current_chunk))

            current_chunk = []

    if current_chunk:

        chunks.append(" ".join(current_chunk))

    return chunks
