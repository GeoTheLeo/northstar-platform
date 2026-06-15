from sentence_transformers import (
    SentenceTransformer,
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def generate_embeddings(
    texts,
):

    return model.encode(
        texts,
        convert_to_tensor=False,
    )