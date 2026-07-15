from sklearn.metrics.pairwise import (
    cosine_similarity,
)

from rag_assistant.embeddings.embedding_generator import (
    generate_embeddings,
)


def retrieve_documents(
    query,
    chunks,
    top_k=3,
):

    chunk_texts = [
        chunk["content"]
        for chunk in chunks
    ]

    chunk_embeddings = (
        generate_embeddings(
            chunk_texts
        )
    )

    query_embedding = (
        generate_embeddings(
            [query]
        )
    )

    similarities = cosine_similarity(
        query_embedding,
        chunk_embeddings,
    )[0]

    ranked_indices = (
        similarities.argsort()[::-1]
    )

    results = []

    for idx in ranked_indices[:top_k]:

        results.append(
            {
                "document":
                chunks[idx]["document"],

                "content":
                chunks[idx]["content"],

                "score":
                round(
                    float(
                        similarities[idx]
                    ),
                    3,
                ),
            }
        )

    return results