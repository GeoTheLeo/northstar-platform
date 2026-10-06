"""
Grounding guardrails: relevance gate, refusals, citations, grounding check.
"""

import json

from rag_assistant.chat.answer_generator import (
    REFUSAL_TOKEN,
    STATUS_ANSWERED,
    STATUS_LLM_UNAVAILABLE,
    STATUS_LOW_RELEVANCE,
    STATUS_NOT_IN_KB,
    STATUS_UNGROUNDED,
    answer_question,
    citations_valid,
    format_answer,
)

RESULTS = [
    {"document": "early_warning_model.txt", "content": "The model is a Random Forest classifier with 100 trees.", "score": 0.67},
    {"document": "learner_segmentation.txt", "content": "The model is KMeans clustering with 4 clusters.", "score": 0.51},
]

GROUNDED = json.dumps({"grounded": True, "unsupported_claims": []})


def test_low_relevance_refuses_without_calling_the_llm(fake_llm):

    fake = fake_llm([])

    low = [dict(RESULTS[0], score=0.1)]

    result = answer_question("What is the capital of France?", low)

    assert result.status == STATUS_LOW_RELEVANCE
    assert fake.calls == []


def test_no_results_refuses(fake_llm):

    fake_llm([])

    assert answer_question("anything", []).status == STATUS_LOW_RELEVANCE


def test_model_refusal_token_is_reported_as_not_in_kb(fake_llm):

    fake = fake_llm([REFUSAL_TOKEN])

    result = answer_question("What does a licence cost?", RESULTS)

    assert result.status == STATUS_NOT_IN_KB
    assert fake.calls == ["answer"]


def test_grounded_cited_answer_is_returned_with_its_sources(fake_llm):

    fake = fake_llm(["It uses a Random Forest with 100 trees [1].", GROUNDED])

    result = answer_question("Which model?", RESULTS)

    assert result.status == STATUS_ANSWERED
    assert result.grounded is True
    assert result.sources == ["early_warning_model.txt"]
    assert fake.calls == ["answer", "grounding_check"]
    assert result.input_tokens == 200
    assert result.cost_usd > 0


def test_ungrounded_answer_is_withheld_and_passages_shown(fake_llm):

    verdict = json.dumps({"grounded": False, "unsupported_claims": ["accuracy is 97%"]})

    fake_llm(["It uses a Random Forest with 97% accuracy [1].", verdict])

    result = answer_question("Which model?", RESULTS)

    assert result.status == STATUS_UNGROUNDED
    assert result.unsupported_claims == ["accuracy is 97%"]
    assert "97%" not in result.answer
    assert "Random Forest classifier with 100 trees" in result.answer


def test_answer_without_citations_is_withheld_without_a_judge_call(fake_llm):

    fake = fake_llm(["It uses a Random Forest."])

    result = answer_question("Which model?", RESULTS)

    assert result.status == STATUS_UNGROUNDED
    assert fake.calls == ["answer"]


def test_citation_to_a_missing_source_is_withheld(fake_llm):

    fake_llm(["It uses a Random Forest [7]."])

    assert answer_question("Which model?", RESULTS).status == STATUS_UNGROUNDED


def test_judge_outage_keeps_answer_but_marks_it_unverified(fake_llm):

    fake_llm(["It uses a Random Forest [1].", RuntimeError("judge down")])

    result = answer_question("Which model?", RESULTS)

    assert result.status == STATUS_ANSWERED
    assert result.grounded is None
    assert "not verified" in format_answer(result)


def test_generation_outage_falls_back_to_retrieved_passages(fake_llm):

    fake_llm([RuntimeError("provider down")])

    result = answer_question("Which model?", RESULTS)

    assert result.status == STATUS_LLM_UNAVAILABLE
    assert "Random Forest classifier" in result.answer


def test_citations_valid():

    assert citations_valid("A [1]. B [2][1].", 2)
    assert not citations_valid("No citations.", 2)
    assert not citations_valid("Out of range [3].", 2)
