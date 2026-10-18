"""Load the persona panel and scenario bank, and render scenario prompts."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "config" / "agent_panel.yaml"
SCENARIOS = ROOT / "config" / "shopping_scenarios.yaml"


def load_panel(path: Path = PANEL) -> list[dict[str, Any]]:
    return yaml.safe_load(path.read_text())["personas"]


def load_scenarios(path: Path = SCENARIOS) -> tuple[dict[str, str], list[dict[str, Any]]]:
    data = yaml.safe_load(path.read_text())
    return data["templates"], data["scenarios"]


def render(templates: dict[str, str], scenario: dict[str, Any]) -> str:
    template = templates[scenario.get("template", "shopping")]
    return " ".join(template.format(**scenario).split())


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]


def select(items: list[dict[str, Any]], wanted: str) -> list[dict[str, Any]]:
    if wanted == "all":
        return items
    ids = [w.strip() for w in wanted.split(",") if w.strip()]
    known = {i["id"] for i in items}
    unknown = [i for i in ids if i not in known]
    if unknown:
        raise SystemExit(f"unknown id(s): {', '.join(unknown)}. Known: {', '.join(sorted(known))}")
    return [i for i in items if i["id"] in ids]
