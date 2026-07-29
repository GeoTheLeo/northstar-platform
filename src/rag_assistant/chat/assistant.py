from rag_assistant.chat.answer_generator import (
    generate_answer,
)
from rag_assistant.chat.copilot import (
    generate_executive_brief,
)
from rag_assistant.ingestion.document_loader import (
    load_documents,
)
from rag_assistant.retrieval.retriever import (
    retrieve_documents,
)


def ask_assistant(question):

    question_lower = question.lower()

    if "executive briefing" in question_lower:

        return generate_executive_brief()

    if "executive summary" in question_lower:

        return generate_executive_brief()

    if "platform status" in question_lower:

        return generate_executive_brief()

    chunks = load_documents()

    results = retrieve_documents(
        question,
        chunks,
    )

    return generate_answer(
        question,
        results,
    )
