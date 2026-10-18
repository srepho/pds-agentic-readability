"""Runner and config tests. Invariants: every scenario renders to a single-line consumer prompt with no
unfilled placeholders and no mention of PDSs; a dry run never builds a client or sends anything; personas
without credentials are skipped, not failed; plan size = personas x scenarios x repeats."""
import importlib.util
from pathlib import Path

import pytest

from pds_agents import config

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runner", ROOT / "scripts" / "run_shopping_agents.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

KEYS = ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY",
        "OPENROUTER_API_KEY"]


@pytest.fixture
def no_keys(monkeypatch):
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


def test_scenarios_render_cleanly():
    templates, scenarios = config.load_scenarios()
    ids = [s["id"] for s in scenarios]
    assert len(ids) == len(set(ids))
    for s in scenarios:
        prompt = config.render(templates, s)
        assert "{" not in prompt and "\n" not in prompt
        assert "PDS" not in prompt and "disclosure" not in prompt.lower()


def test_panel_entries_are_buildable():
    from pds_agents import providers
    for p in config.load_panel():
        assert p["provider"] in providers.PROVIDERS
        if p["provider"] != "openrouter":
            assert p.get("openrouter_model"), p["id"]


def test_dry_run_plans_without_calling(no_keys, monkeypatch, capsys):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: None)
    rc = runner.main(["--personas", "selfhosted_minimax,anthropic_opus", "--scenarios",
                      "car_young_commuter_nsw,travel_family_japan", "--repeats", "3"])
    out = capsys.readouterr().out
    assert rc == 0 and "6 calls planned" in out and "dry run" in out
    assert "anthropic_opus (no ANTHROPIC_API_KEY" in out


def test_via_openrouter_plans_every_persona(no_keys, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    args = runner.parse_args(["--via-openrouter", "--scenarios", "home_flood_prone_qld"])
    jobs, skipped = runner.plan(args)
    assert skipped == [] and len(jobs) == len(config.load_panel())


def test_unknown_id_is_rejected():
    with pytest.raises(SystemExit):
        config.select([{"id": "a"}], "a,b")


def test_execute_writes_log_and_summary(no_keys, monkeypatch, tmp_path):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: None)
    monkeypatch.setattr(runner.time, "sleep", lambda s: None)
    from pds_agents import providers
    from pds_agents.types import AgentResult, Citation

    def fake_ask(self, prompt):
        return AgentResult(persona=self.persona, provider=self.name, model=self.model, text="Go with Youi.",
                           citations=[Citation("https://www.youi.com.au/documents/home-pds")])

    monkeypatch.setattr(providers.OpenRouterProvider, "ask", fake_ask)
    rc = runner.main(["--personas", "selfhosted_glm", "--scenarios", "home_suburban_wa", "--execute",
                      "--out", str(tmp_path)])
    logs = list(tmp_path.glob("*.jsonl")); summaries = list(tmp_path.glob("*.summary.csv"))
    assert rc == 0 and len(logs) == 1 and len(summaries) == 1
    text = summaries[0].read_text()
    assert "youi" in text and ",1,0," in text.replace("\r", "")  # one PDS citation, zero comparator citations
