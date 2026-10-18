"""Normalised result types shared by every provider adapter."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Citation:
    url: str
    title: str = ""


@dataclass
class AgentResult:
    persona: str
    provider: str
    model: str
    text: str = ""
    citations: list[Citation] = field(default_factory=list)
    search_queries: list[str] = field(default_factory=list)
    stop_reason: str | None = None
    served_model: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)
    latency_s: float = 0.0
    error: str | None = None
    raw: Any = None


def get(obj: Any, name: str, default: Any = None) -> Any:
    """Read a field from an SDK object or a plain dict."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def dump(obj: Any) -> Any:
    """Best-effort JSON-serialisable view of an SDK response for the raw log."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [dump(o) for o in obj]
    if isinstance(obj, dict):
        return {k: dump(v) for k, v in obj.items()}
    for method in ("model_dump", "to_dict"):
        fn = getattr(obj, method, None)
        if callable(fn):
            try:
                return fn()
            except TypeError:
                continue
    if hasattr(obj, "__dict__"):
        return {k: dump(v) for k, v in vars(obj).items() if not k.startswith("_")}
    return repr(obj)


def dedupe(citations: list[Citation]) -> list[Citation]:
    seen: set[str] = set()
    out = []
    for c in citations:
        if c.url and c.url not in seen:
            seen.add(c.url)
            out.append(c)
    return out
