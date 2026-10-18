"""Provider adapters. Each adapter sends one consumer prompt with the provider's web search enabled
and normalises the response into an AgentResult.

Adapter sources (checked 18 Oct 2026):
- Anthropic: Messages API, server tool web_search_20260209, server-side fallbacks "default".
- OpenAI: Responses API with the "web_search" tool.
- Google: google-genai Interactions API with the "google_search" tool.
- OpenRouter: OpenAI-compatible chat completions with the "web" plugin. Uses each vendor's native search
  for OpenAI, Anthropic, Google and Perplexity models, and Exa search for other models.

SDK clients are imported lazily so a missing optional SDK only disables its own provider.
"""
from __future__ import annotations

import os
import time
from typing import Any

from .types import AgentResult, Citation, dedupe, dump, get

AU_LOCATION = {"type": "approximate", "country": "AU"}

# Models that accept Anthropic's server-side fallback in its "default" form. Haiku has no server-side
# fallback and Opus 4.6 predates it.
ANTHROPIC_FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5", "claude-fable-5-1"}
MAX_PAUSE_CONTINUATIONS = 5


class Provider:
    name = "base"
    env_keys: tuple[str, ...] = ()

    def __init__(self, persona: str, model: str, options: dict[str, Any] | None = None, client: Any = None):
        self.persona = persona
        self.model = model
        self.options = options or {}
        self._client = client

    def available(self) -> bool:
        return self._client is not None or any(os.environ.get(k) for k in self.env_keys)

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = self._make_client()
        return self._client

    def _make_client(self) -> Any:
        raise NotImplementedError

    def _call(self, prompt: str) -> Any:
        raise NotImplementedError

    def normalise(self, response: Any) -> AgentResult:
        raise NotImplementedError

    def _empty(self) -> AgentResult:
        return AgentResult(persona=self.persona, provider=self.name, model=self.model)

    def ask(self, prompt: str) -> AgentResult:
        start = time.perf_counter()
        try:
            response = self._call(prompt)
            result = self.normalise(response)
            result.raw = dump(response)
        except Exception as e:  # noqa: BLE001 - a failed call is recorded as a result, not raised
            result = self._empty()
            result.error = f"{type(e).__name__}: {e}"[:2000]
        result.latency_s = round(time.perf_counter() - start, 2)
        return result


class AnthropicProvider(Provider):
    name = "anthropic"
    env_keys = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")

    def _make_client(self) -> Any:
        import anthropic

        return anthropic.Anthropic()

    def request_kwargs(self) -> dict[str, Any]:
        tool = {
            "type": "web_search_20260209",
            "name": "web_search",
            "max_uses": int(self.options.get("max_searches", 5)),
            "user_location": AU_LOCATION,
        }
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": int(self.options.get("max_tokens", 16000)),
            "tools": [tool],
            "output_config": {"effort": self.options.get("effort", "medium")},
        }
        if self.model in ANTHROPIC_FALLBACK_MODELS:
            kwargs["betas"] = ["server-side-fallback-2026-07-01"]
            kwargs["fallbacks"] = "default"
        return kwargs

    def _call(self, prompt: str) -> list[Any]:
        kwargs = self.request_kwargs()
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        responses = []
        for _ in range(MAX_PAUSE_CONTINUATIONS + 1):
            response = self.client.beta.messages.create(messages=messages, **kwargs)
            responses.append(response)
            if response.stop_reason != "pause_turn":
                break
            # A long server-tool turn paused: re-send with the partial turn so the model resumes it.
            messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": response.content}]
        return responses

    def normalise(self, response: Any) -> AgentResult:
        responses = response if isinstance(response, list) else [response]
        result = self._empty()
        texts, cites, queries = [], [], []
        usage = {"input_tokens": 0, "output_tokens": 0, "web_search_requests": 0}
        for r in responses:
            for block in get(r, "content") or []:
                btype = get(block, "type")
                if btype == "text":
                    texts.append(get(block, "text") or "")
                    for c in get(block, "citations") or []:
                        if get(c, "url"):
                            cites.append(Citation(get(c, "url"), get(c, "title") or ""))
                elif btype == "server_tool_use":
                    q = get(get(block, "input") or {}, "query")
                    if q:
                        queries.append(q)
                elif btype == "web_search_tool_result":
                    content = get(block, "content")
                    if isinstance(content, list):  # an error result is a single object, not a list
                        cites.extend(Citation(get(i, "url"), get(i, "title") or "") for i in content if get(i, "url"))
            u = get(r, "usage")
            usage["input_tokens"] += get(u, "input_tokens", 0) or 0
            usage["output_tokens"] += get(u, "output_tokens", 0) or 0
            usage["web_search_requests"] += get(get(u, "server_tool_use"), "web_search_requests", 0) or 0
        last = responses[-1]
        result.text = "".join(texts).strip()
        result.citations = dedupe(cites)
        result.search_queries = queries
        result.stop_reason = get(last, "stop_reason")
        result.served_model = get(last, "model")
        result.usage = usage
        if result.stop_reason == "refusal":
            result.error = f"refusal: {dump(get(last, 'stop_details'))}"
        return result


class OpenAIProvider(Provider):
    name = "openai"
    env_keys = ("OPENAI_API_KEY",)

    def _make_client(self) -> Any:
        from openai import OpenAI

        return OpenAI()

    def _call(self, prompt: str) -> Any:
        return self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search", "user_location": AU_LOCATION}],
            input=prompt,
        )

    def normalise(self, response: Any) -> AgentResult:
        result = self._empty()
        cites, queries = [], []
        for item in get(response, "output") or []:
            itype = get(item, "type")
            if itype == "web_search_call":
                action = get(item, "action")
                q = get(action, "query")
                queries.extend([q] if q else list(get(action, "queries") or []))
            elif itype == "message":
                for part in get(item, "content") or []:
                    for a in get(part, "annotations") or []:
                        if get(a, "type") == "url_citation" and get(a, "url"):
                            cites.append(Citation(get(a, "url"), get(a, "title") or ""))
        u = get(response, "usage")
        result.text = (get(response, "output_text") or "").strip()
        result.citations = dedupe(cites)
        result.search_queries = queries
        result.stop_reason = get(response, "status")
        result.served_model = get(response, "model")
        result.usage = {"input_tokens": get(u, "input_tokens", 0), "output_tokens": get(u, "output_tokens", 0)}
        return result


class GeminiProvider(Provider):
    name = "gemini"
    env_keys = ("GEMINI_API_KEY", "GOOGLE_API_KEY")

    def _make_client(self) -> Any:
        from google import genai

        return genai.Client()

    def _call(self, prompt: str) -> Any:
        return self.client.interactions.create(model=self.model, input=prompt, tools=[{"type": "google_search"}])

    def normalise(self, response: Any) -> AgentResult:
        result = self._empty()
        cites, queries = [], []
        for step in get(response, "steps") or []:
            stype = get(step, "type")
            if stype == "google_search_call":
                queries.extend(get(get(step, "arguments") or {}, "queries") or [])
            elif stype == "model_output":
                for block in get(step, "content") or []:
                    for a in get(block, "annotations") or []:
                        if get(a, "type") == "url_citation" and get(a, "url"):
                            cites.append(Citation(get(a, "url"), get(a, "title") or ""))
        result.text = (get(response, "output_text") or "").strip()
        result.citations = dedupe(cites)
        result.search_queries = list(queries)
        result.stop_reason = get(response, "status")
        result.served_model = get(response, "model") or self.model
        result.usage = dump(get(response, "usage")) or {}
        return result


class OpenRouterProvider(Provider):
    name = "openrouter"
    env_keys = ("OPENROUTER_API_KEY",)
    base_url = "https://openrouter.ai/api/v1"

    def _make_client(self) -> Any:
        from openai import OpenAI

        return OpenAI(base_url=self.base_url, api_key=os.environ["OPENROUTER_API_KEY"])

    def plugin(self) -> dict[str, Any]:
        plugin: dict[str, Any] = {"id": "web"}
        for key in ("engine", "max_results"):
            if key in self.options:
                plugin[key] = self.options[key]
        return plugin

    def _call(self, prompt: str) -> Any:
        return self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"plugins": [self.plugin()]},
        )

    def normalise(self, response: Any) -> AgentResult:
        result = self._empty()
        choice = (get(response, "choices") or [None])[0]
        message = get(choice, "message")
        cites = []
        for a in get(message, "annotations") or []:
            uc = get(a, "url_citation") or a
            if get(a, "type") == "url_citation" and get(uc, "url"):
                cites.append(Citation(get(uc, "url"), get(uc, "title") or ""))
        u = get(response, "usage")
        result.text = (get(message, "content") or "").strip()
        result.citations = dedupe(cites)
        result.stop_reason = get(choice, "finish_reason")
        result.served_model = get(response, "model")
        result.usage = {"input_tokens": get(u, "prompt_tokens", 0), "output_tokens": get(u, "completion_tokens", 0)}
        return result


PROVIDERS: dict[str, type[Provider]] = {
    p.name: p for p in (AnthropicProvider, OpenAIProvider, GeminiProvider, OpenRouterProvider)
}


def build(persona: dict[str, Any], via_openrouter: bool = False, client: Any = None) -> Provider:
    """Create the adapter for a persona entry from config/agent_panel.yaml."""
    options = dict(persona.get("options") or {})
    if via_openrouter and persona["provider"] != "openrouter":
        slug = persona.get("openrouter_model")
        if not slug:
            raise ValueError(f"persona {persona['id']} has no openrouter_model for --via-openrouter")
        return OpenRouterProvider(persona["id"], slug, options, client)
    cls = PROVIDERS[persona["provider"]]
    return cls(persona["id"], persona["model"], options, client)
