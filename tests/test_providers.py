"""Adapter tests with fake SDK responses shaped like each provider's documented output.
Invariant: every adapter maps its provider's answer text, cited URLs and search queries into the same
AgentResult fields, and a failed call becomes a recorded error rather than an exception."""
from types import SimpleNamespace as NS

import pytest

from pds_agents import providers


def anthropic_response(content, stop="end_turn", searches=1):
    usage = NS(input_tokens=100, output_tokens=50, server_tool_use=NS(web_search_requests=searches))
    return NS(content=content, stop_reason=stop, model="claude-opus-5-5", usage=usage, stop_details=None)


def test_anthropic_normalise_text_citations_queries():
    resp = anthropic_response([
        NS(type="server_tool_use", input={"query": "best home insurance Brisbane flood"}),
        NS(type="web_search_tool_result", content=[NS(type="web_search_result", url="https://www.suncorp.com.au/x", title="S")]),
        NS(type="text", text="Consider Suncorp.", citations=[
            NS(type="web_search_result_location", url="https://www.canstar.com.au/y", title="C", cited_text="..."),
            NS(type="web_search_result_location", url="https://www.suncorp.com.au/x", title="S", cited_text="...")]),
    ])
    r = providers.AnthropicProvider("p", "claude-opus-5-5", client=object()).normalise([resp])
    assert r.text == "Consider Suncorp."
    assert [c.url for c in r.citations] == ["https://www.suncorp.com.au/x", "https://www.canstar.com.au/y"]
    assert r.search_queries == ["best home insurance Brisbane flood"]
    assert r.usage["web_search_requests"] == 1 and r.stop_reason == "end_turn"


def test_anthropic_search_error_object_is_not_iterated():
    resp = anthropic_response([NS(type="web_search_tool_result", content=NS(type="web_search_tool_result_error",
                                                                          error_code="max_uses_exceeded")),
                               NS(type="text", text="ok", citations=None)])
    r = providers.AnthropicProvider("p", "claude-opus-5-5", client=object()).normalise([resp])
    assert r.citations == [] and r.text == "ok"


def test_anthropic_pause_turn_is_resumed_and_text_concatenated():
    calls = []

    class Msgs:
        def create(self, **kw):
            calls.append(kw)
            if len(calls) == 1:
                return anthropic_response([NS(type="text", text="Part one. ", citations=None)], stop="pause_turn")
            return anthropic_response([NS(type="text", text="Part two.", citations=None)])

    client = NS(beta=NS(messages=Msgs()))
    r = providers.AnthropicProvider("p", "claude-opus-5-5", client=client).ask("q")
    assert len(calls) == 2
    assert calls[1]["messages"][1]["role"] == "assistant"
    assert r.text == "Part one. Part two." and r.error is None
    assert r.usage["input_tokens"] == 200


@pytest.mark.parametrize("model,has_fallback", [("claude-opus-5-5", True), ("claude-sonnet-5-5", True),
                                                ("claude-haiku-5-5", False), ("claude-opus-4-6", False)])
def test_anthropic_fallback_only_where_supported(model, has_fallback):
    kw = providers.AnthropicProvider("p", model, client=object()).request_kwargs()
    assert ("fallbacks" in kw) is has_fallback
    assert kw["tools"][0]["type"] == "web_search_20260209"
    assert kw["tools"][0]["user_location"]["country"] == "AU"


def test_anthropic_refusal_recorded_as_error():
    resp = anthropic_response([], stop="refusal")
    r = providers.AnthropicProvider("p", "claude-opus-5-5", client=object()).normalise([resp])
    assert r.error and r.error.startswith("refusal")


def test_openai_normalise():
    resp = {"output_text": "Try AAMI.", "status": "completed", "model": "gpt-6.1-sol",
            "usage": {"input_tokens": 10, "output_tokens": 5},
            "output": [{"type": "web_search_call", "action": {"query": "aami car"}},
                       {"type": "message", "content": [{"type": "output_text", "text": "Try AAMI.", "annotations": [
                           {"type": "url_citation", "url": "https://www.aami.com.au/car", "title": "AAMI"}]}]}]}
    r = providers.OpenAIProvider("p", "gpt-6.1-sol", client=object()).normalise(resp)
    assert r.text == "Try AAMI." and r.citations[0].url == "https://www.aami.com.au/car"
    assert r.search_queries == ["aami car"]


def test_gemini_normalise():
    resp = {"output_text": "Youi is good.", "status": "completed",
            "steps": [{"type": "google_search_call", "arguments": {"queries": ["youi home", "youi pds"]}},
                      {"type": "model_output", "content": [{"type": "text", "text": "Youi is good.", "annotations": [
                          {"type": "url_citation", "url": "https://www.youi.com.au/pds", "title": "Youi"}]}]}]}
    r = providers.GeminiProvider("p", "gemini-3.8-flash", client=object()).normalise(resp)
    assert r.search_queries == ["youi home", "youi pds"] and r.citations[0].title == "Youi"


def test_openrouter_call_sends_web_plugin_and_normalises():
    sent = {}

    class Completions:
        def create(self, **kw):
            sent.update(kw)
            return {"model": "minimax/minimax-m3", "usage": {"prompt_tokens": 7, "completion_tokens": 3},
                    "choices": [{"finish_reason": "stop", "message": {"content": "NRMA.", "annotations": [
                        {"type": "url_citation", "url_citation": {"url": "https://www.nrma.com.au/a", "title": "N"}}]}}]}

    client = NS(chat=NS(completions=Completions()))
    r = providers.OpenRouterProvider("p", "minimax/minimax-m3", {"max_results": 3}, client=client).ask("q")
    assert sent["extra_body"]["plugins"] == [{"id": "web", "max_results": 3}]
    assert r.text == "NRMA." and r.citations[0].url == "https://www.nrma.com.au/a" and r.raw is not None


def test_failed_call_becomes_error_result():
    class Boom:
        def create(self, **kw):
            raise RuntimeError("network down")

    r = providers.OpenRouterProvider("p", "x/y", client=NS(chat=NS(completions=Boom()))).ask("q")
    assert r.error == "RuntimeError: network down" and r.text == "" and r.latency_s >= 0


def test_build_via_openrouter_swaps_provider_and_requires_slug():
    persona = {"id": "a", "provider": "anthropic", "model": "claude-opus-5-5", "openrouter_model": "anthropic/claude-opus-5.5"}
    p = providers.build(persona, via_openrouter=True)
    assert isinstance(p, providers.OpenRouterProvider) and p.model == "anthropic/claude-opus-5.5"
    with pytest.raises(ValueError):
        providers.build({"id": "b", "provider": "openai", "model": "m"}, via_openrouter=True)
