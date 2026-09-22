import os

from openai import OpenAI

MODEL = "gpt-4o-mini"

_client = None


def _get_client():
    global _client

    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _client


def generate_answer(
    question,
    results,
):

    if not results:

        return "No relevant knowledge found."

    sources = set()

    context_blocks = []

    for result in results:

        clean_text = result["content"].replace("\n", " ").replace("  ", " ")

        context_blocks.append(f"[{result['document']}]\n{clean_text}")

        sources.add(result["document"])

    context = "\n\n".join(context_blocks)

    try:

        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the NorthStar AI Knowledge Assistant. Answer the user's question "
                        "using only the context provided below. Be concise and specific. If the "
                        "context doesn't contain the answer, say so plainly rather than guessing."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                },
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content

    except Exception as e:

        print("LLM generation failed:", e)

        answer = (
            "(AI generation unavailable — showing retrieved context directly)\n\n"
            + "\n\n".join(block.split("\n", 1)[1] for block in context_blocks)
        )

    source_text = "\n".join(f"- {source}" for source in sources)

    return (
        f"\nNorthStar Response\n"
        f"{'=' * 50}\n\n"
        f"{answer}\n\n"
        f"Sources\n"
        f"{'-' * 20}\n"
        f"{source_text}"
    )
