def generate_answer(
    question,
    results,
):

    if not results:

        return (
            "No relevant knowledge found."
        )

    sources = set()

    supporting_points = []

    for result in results:

        clean_text = (
            result["content"]
            .replace("\n", " ")
            .replace("  ", " ")
        )

        supporting_points.append(
            clean_text
        )

        sources.add(
            result["document"]
        )

    answer = "\n\n".join(
        supporting_points
    )

    source_text = "\n".join(
        f"- {source}"
        for source in sources
    )

    return (
        f"\nNorthStar Response\n"
        f"{'=' * 50}\n\n"
        f"{answer}\n\n"
        f"Sources\n"
        f"{'-' * 20}\n"
        f"{source_text}"
    )