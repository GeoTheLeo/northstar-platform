"""
BM25 sparse vectors for the keyword half of hybrid search.

Each chunk becomes a sparse vector of BM25 term-frequency weights; Qdrant
applies the IDF half itself (Modifier.IDF on the sparse vector config), so
rare terms like "KMeans" or "80/20" outweigh common ones. A query is just its
set of terms, each weighted 1.0.

Terms are hashed with CRC32 rather than Python's hash(), which is salted per
process and would scramble the index between restarts.
"""

import re
import zlib
from collections import Counter

from qdrant_client.models import SparseVector

# BM25 term-frequency saturation and length normalisation (standard values).
K1 = 1.2
B = 0.75

# Fixed average chunk length in terms. Chunks are single paragraphs of
# roughly 20-60 terms; a fixed value keeps a live-metrics upsert from
# shifting every other chunk's weights.
AVG_CHUNK_TERMS = 40

STOPWORDS = frozenset(
    "a an and are as at be by can do does for from has have how if in into is it its "
    "of on or so that the their then there these this to was what when where which "
    "who why will with".split()
)


def tokenize(text: str) -> list[str]:

    terms = []

    for term in re.findall(r"[a-z0-9]+", text.lower()):

        if term in STOPWORDS:
            continue

        # Light plural folding, so "segments" matches "segment".
        if len(term) > 3 and term.endswith("s") and not term.endswith("ss"):
            term = term[:-1]

        terms.append(term)

    return terms


def _term_id(term: str) -> int:

    return zlib.crc32(term.encode("utf-8"))


def _vector(weights: dict[int, float]) -> SparseVector:

    indices = sorted(weights)

    return SparseVector(indices=indices, values=[weights[i] for i in indices])


def document_vector(text: str) -> SparseVector:

    terms = tokenize(text)

    length_norm = 1 - B + B * len(terms) / AVG_CHUNK_TERMS

    return _vector(
        {
            _term_id(term): tf * (K1 + 1) / (tf + K1 * length_norm)
            for term, tf in Counter(terms).items()
        }
    )


def query_vector(text: str) -> SparseVector:

    return _vector({_term_id(term): 1.0 for term in set(tokenize(text))})
