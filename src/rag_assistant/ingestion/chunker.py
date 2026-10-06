import re

# Paragraphs shorter than this are merged into the next one, so a lead-in
# ("The platform includes:", a one-line document intro) stays attached to
# the content it introduces instead of becoming a vague chunk of its own.
MIN_CHUNK_CHARS = 120


def _split_sentences(text):

    return re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )


def chunk_text(
    text,
    max_sentences_per_chunk=5,
):
    """
    Paragraph-aware chunking. Each paragraph is one chunk, so a rule and its
    consequence ("If X ... Expected time to impact is Y") never get split
    across chunks. Long paragraphs fall back to sentence windows.
    """

    paragraphs = [
        " ".join(p.split())
        for p in re.split(r"\n\s*\n", text.strip())
        if p.strip()
    ]

    merged = []

    carry = ""

    for paragraph in paragraphs:

        paragraph = f"{carry} {paragraph}".strip()

        if len(paragraph) < MIN_CHUNK_CHARS:

            carry = paragraph

            continue

        carry = ""

        merged.append(paragraph)

    if carry:

        if merged:
            merged[-1] = f"{merged[-1]} {carry}"
        else:
            merged.append(carry)

    chunks = []

    for paragraph in merged:

        sentences = _split_sentences(paragraph)

        for start in range(0, len(sentences), max_sentences_per_chunk):

            chunks.append(" ".join(sentences[start:start + max_sentences_per_chunk]))

    return chunks
