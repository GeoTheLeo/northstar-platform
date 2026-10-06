"""
Shared, traced LLM client for the NorthStar assistants.

Every call emits a GenAI-convention span with model, token usage,
estimated cost, and latency, so cost and failures are visible per request.
"""

import os
from dataclasses import dataclass

from openai import OpenAI

from rag_assistant.observability.tracing import estimate_cost_usd, get_tracer

MODEL = "gpt-4o-mini"

_client = None


@dataclass(frozen=True)
class LLMResponse:
    """
    Text plus the usage numbers the caller may want to surface.
    """

    text: str

    input_tokens: int

    output_tokens: int

    cost_usd: float | None


def _get_client() -> OpenAI:
    global _client

    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _client


def chat(
    messages: list[dict],
    temperature: float = 0.2,
    json_output: bool = False,
    purpose: str = "generation",
) -> LLMResponse:
    """
    Run one chat completion inside a traced span. Raises on provider errors;
    callers decide the fallback.
    """

    with get_tracer().start_as_current_span(f"chat {MODEL}") as span:

        span.set_attribute("gen_ai.operation.name", "chat")
        span.set_attribute("gen_ai.provider.name", "openai")
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", MODEL)
        span.set_attribute("gen_ai.request.temperature", temperature)
        span.set_attribute("northstar.llm.purpose", purpose)

        kwargs = {}

        if json_output:
            kwargs["response_format"] = {"type": "json_object"}

        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )

        usage = response.usage

        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        cost = estimate_cost_usd(MODEL, input_tokens, output_tokens)

        span.set_attribute("gen_ai.response.model", response.model)
        span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", output_tokens)

        if cost is not None:
            span.set_attribute("northstar.llm.cost_usd", cost)

        return LLMResponse(
            text=response.choices[0].message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
