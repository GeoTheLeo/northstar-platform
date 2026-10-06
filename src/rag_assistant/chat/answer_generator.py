"""
Grounded answer generation for the NorthStar Knowledge Assistant.

Three guardrails keep answers tied to the knowledge base:

1. Relevance gate: if no retrieved chunk clears MIN_RELEVANCE, the assistant
   says it doesn't know, without calling the LLM at all.
2. Cited generation: the model must cite a numbered source for each claim,
   or reply with REFUSAL_TOKEN when the context doesn't hold the answer.
3. Grounding check: a second, deterministic (temperature 0) LLM pass judges
   whether every claim is supported by the cited context. Unsupported
   answers are withheld and the relevant passages are shown instead.
"""

import json
import re
from dataclasses import dataclass, field

from rag_assistant import llm
from rag_assistant.observability.tracing import get_tracer

# Calibrated with rag_assistant/evals/run_evals.py: on the golden set, the
# lowest answerable top score is ~0.40 and the highest off-topic one ~0.11.
# 0.25 sits midway, leaving margin on both sides. Near-domain questions clear
# this gate by design; the model refusal and grounding check handle those.
MIN_RELEVANCE = 0.25

REFUSAL_TOKEN = "NOT_IN_KNOWLEDGE_BASE"

GENERATION_PROMPT = (
    "You are the NorthStar AI Knowledge Assistant. Answer the user's question "
    "using only the numbered context below. Be concise and specific. After each "
    "sentence, cite the source number(s) it relies on, like [1] or [2][3]. "
    f"If the context does not contain the answer, reply with exactly {REFUSAL_TOKEN} "
    "and nothing else. Never use outside knowledge."
)

GROUNDING_PROMPT = (
    "You check answers from a retrieval-augmented assistant. Given the numbered "
    "context and an answer, decide whether every factual claim in the answer is "
    "directly supported by the context. Paraphrase is fine; added facts, numbers, "
    "or conclusions not stated in the context are not. Reply as JSON: "
    '{"grounded": true|false, "unsupported_claims": ["..."]}'
)

STATUS_ANSWERED = "answered"
STATUS_LOW_RELEVANCE = "refused_low_relevance"
STATUS_NOT_IN_KB = "refused_not_in_kb"
STATUS_UNGROUNDED = "withheld_ungrounded"
STATUS_LLM_UNAVAILABLE = "llm_unavailable"


@dataclass
class AnswerResult:
    """
    The answer plus everything needed to explain and audit it.
    """

    status: str

    answer: str

    results: list[dict]

    sources: list[str] = field(default_factory=list)

    grounded: bool | None = None

    unsupported_claims: list[str] = field(default_factory=list)

    input_tokens: int = 0

    output_tokens: int = 0

    cost_usd: float = 0.0

    trace_id: str | None = None

    latency_ms: float | None = None

    @property
    def top_score(self) -> float | None:

        return self.results[0]["score"] if self.results else None


def numbered_context(results: list[dict]) -> str:

    return "\n\n".join(
        f"[{i}] ({r['document']})\n{' '.join(r['content'].split())}"
        for i, r in enumerate(results, start=1)
    )


def cited_sources(answer: str) -> set[int]:

    return {int(n) for n in re.findall(r"\[(\d+)\]", answer)}


def citations_valid(answer: str, num_results: int) -> bool:
    """
    At least one citation, and every citation points at a real source.
    """

    cited = cited_sources(answer)

    return bool(cited) and all(1 <= n <= num_results for n in cited)


def passages_fallback(results: list[dict]) -> str:

    return "\n\n".join(
        f"> {' '.join(r['content'].split())}\n> — *{r['document']}*" for r in results
    )


def _add_usage(result: AnswerResult, response: llm.LLMResponse) -> None:

    result.input_tokens += response.input_tokens
    result.output_tokens += response.output_tokens
    result.cost_usd += response.cost_usd or 0.0


def check_grounding(context: str, answer: str) -> tuple[bool, list[str], llm.LLMResponse]:

    with get_tracer().start_as_current_span("rag.grounding_check") as span:

        response = llm.chat(
            [
                {"role": "system", "content": GROUNDING_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nAnswer:\n{answer}"},
            ],
            temperature=0.0,
            json_output=True,
            purpose="grounding_check",
        )

        verdict = json.loads(response.text)

        grounded = bool(verdict.get("grounded"))
        unsupported = [str(c) for c in verdict.get("unsupported_claims", [])]

        span.set_attribute("northstar.rag.grounded", grounded)
        span.set_attribute("northstar.rag.unsupported_claims", len(unsupported))

        return grounded, unsupported, response


def answer_question(
    question: str,
    results: list[dict],
    min_relevance: float = MIN_RELEVANCE,
) -> AnswerResult:
    """
    Apply the three guardrails and return a structured, auditable result.
    """

    with get_tracer().start_as_current_span("rag.generate") as span:

        result = AnswerResult(status=STATUS_ANSWERED, answer="", results=results)

        # 1. Relevance gate: no LLM call when nothing relevant was retrieved.
        if not results or results[0]["score"] < min_relevance:

            result.status = STATUS_LOW_RELEVANCE
            result.answer = (
                "I don't have information about that in the NorthStar knowledge base."
            )

            span.set_attribute("northstar.rag.status", result.status)

            return result

        context = numbered_context(results)

        # 2. Cited generation.
        try:
            response = llm.chat(
                [
                    {"role": "system", "content": GENERATION_PROMPT},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
                ],
                temperature=0.2,
                purpose="answer",
            )

        except Exception as e:

            print("LLM generation failed:", e)

            result.status = STATUS_LLM_UNAVAILABLE
            result.answer = (
                "(AI generation unavailable — showing retrieved context directly)\n\n"
                + passages_fallback(results)
            )
            result.sources = sorted({r["document"] for r in results})

            span.set_attribute("northstar.rag.status", result.status)

            return result

        _add_usage(result, response)

        answer = response.text.strip()

        if REFUSAL_TOKEN in answer:

            result.status = STATUS_NOT_IN_KB
            result.answer = (
                "The NorthStar knowledge base doesn't answer that question."
            )

            span.set_attribute("northstar.rag.status", result.status)

            return result

        # 3. Grounding check. Missing or invalid citations fail it outright.
        if not citations_valid(answer, len(results)):

            result.grounded = False
            result.unsupported_claims = ["Answer did not cite valid sources."]

        else:
            try:
                grounded, unsupported, verdict_response = check_grounding(context, answer)

                _add_usage(result, verdict_response)

                result.grounded = grounded
                result.unsupported_claims = unsupported

            except Exception as e:

                # Judge outage: keep the cited answer but leave it unverified
                # (grounded stays None), which the UI labels explicitly.
                print("Grounding check failed:", e)

        if result.grounded is False:

            result.status = STATUS_UNGROUNDED
            result.answer = (
                "I found related material but couldn't verify an answer against it, "
                "so here are the most relevant passages:\n\n"
                + passages_fallback(results)
            )
            result.sources = sorted({r["document"] for r in results})

        else:
            result.answer = answer
            result.sources = sorted(
                {results[n - 1]["document"] for n in cited_sources(answer)}
            )

        span.set_attribute("northstar.rag.status", result.status)

        if result.grounded is not None:
            span.set_attribute("northstar.rag.grounded", result.grounded)

        return result


def format_answer(result: AnswerResult) -> str:
    """
    Markdown rendering used by the CLI and the Streamlit chat.
    """

    text = f"{result.answer}"

    if result.status == STATUS_ANSWERED and result.grounded is None:
        text += "\n\n*(Grounding check unavailable — answer not verified.)*"

    if result.sources:
        text += "\n\n**Sources**\n" + "\n".join(f"- {s}" for s in result.sources)

    return text


def generate_answer(
    question,
    results,
):

    return format_answer(answer_question(question, results))
