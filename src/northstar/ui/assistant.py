"""
NorthStar Knowledge Assistant View

Provides the conversational interface for the
NorthStar RAG assistant.
"""

import streamlit as st

from rag_assistant.chat.answer_generator import (
    AnswerResult,
    format_answer,
)
from rag_assistant.chat.assistant import (
    BRIEFING_TRIGGERS,
    answer_with_rag,
)
from rag_assistant.chat.copilot import (
    generate_executive_brief,
)

STATUS_LABELS = {
    "answered": ":green[:material/verified: Answered from sources]",
    "refused_low_relevance": ":gray[:material/block: No relevant sources, LLM not called]",
    "refused_not_in_kb": ":gray[:material/block: Sources don't contain the answer]",
    "withheld_ungrounded": ":orange[:material/gpp_maybe: Answer withheld, failed grounding check]",
    "llm_unavailable": ":red[:material/cloud_off: LLM unavailable, showing passages]",
}


def trace_summary(result: AnswerResult) -> dict:
    """
    Plain-dict trace for session state and display.
    """

    return {
        "status": result.status,
        "grounded": result.grounded,
        "unsupported_claims": result.unsupported_claims,
        "retrieved": [
            {"document": r["document"], "score": r["score"]}
            for r in result.results
        ],
        "latency_ms": result.latency_ms,
        "tokens": result.input_tokens + result.output_tokens,
        "cost_usd": result.cost_usd,
        "trace_id": result.trace_id,
    }


def render_trace(trace: dict) -> None:
    """
    Per-answer observability: what was retrieved, what the guardrails
    decided, and what it cost.
    """

    with st.expander("Answer trace", icon=":material/timeline:"):

        st.markdown(STATUS_LABELS.get(trace["status"], trace["status"]))

        if trace["grounded"] is True:
            st.caption("Grounding check: every claim supported by the cited sources.")
        elif trace["grounded"] is None and trace["status"] == "answered":
            st.caption("Grounding check unavailable: answer not verified.")

        for claim in trace["unsupported_claims"]:
            st.caption(f"Unsupported: {claim}")

        with st.container(horizontal=True):
            st.metric("Latency", f"{trace['latency_ms']:.0f} ms")
            st.metric("Tokens", trace["tokens"])
            st.metric("Cost", f"${trace['cost_usd']:.5f}")

        st.dataframe(
            trace["retrieved"],
            column_config={
                "document": "Retrieved source",
                "score": st.column_config.ProgressColumn(
                    "Similarity", min_value=0.0, max_value=1.0, format="%.3f"
                ),
            },
            hide_index=True,
        )

        st.caption(f"Trace ID `{trace['trace_id']}` · OpenTelemetry, GenAI conventions")


def render_assistant() -> None:
    """
    Render the NorthStar Knowledge Assistant.
    """

    st.header("💬 Knowledge Assistant")

    st.markdown(
        """
Ask questions about the NorthStar platform using
Retrieval-Augmented Generation (RAG).

The assistant retrieves relevant institutional knowledge
before generating each response.
"""
    )

    st.write("")

    left, right = st.columns(
        [4, 1],
        gap="large",
    )

    with left:

        st.info(
            """
**Capabilities**

• Semantic search over a Qdrant vector index

• Retrieval-Augmented Generation (RAG) with cited sources

• Grounding guardrails: answers are verified against sources

• OpenTelemetry tracing of every answer
"""
        )

    with right:

        st.metric(
            label="Knowledge Base",
            value="Online",
            delta="Indexed",
            border=True,
        )

    st.divider()

    if "messages" not in st.session_state:

        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

            if message.get("trace"):
                render_trace(message["trace"])

    question = st.chat_input(
        "Ask NorthStar a question...",
        submit_mode="disable",
    )

    if not question:

        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    with st.spinner(
        "Searching institutional knowledge..."
    ):

        if any(t in question.lower() for t in BRIEFING_TRIGGERS):

            response = generate_executive_brief()
            trace = None

        else:

            result = answer_with_rag(question)
            response = format_answer(result)
            trace = trace_summary(result)

    with st.chat_message(
        "assistant"
    ):

        st.markdown(
            response
        )

        if trace:
            render_trace(trace)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "trace": trace,
        }
    )