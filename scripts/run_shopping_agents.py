"""Ask web-enabled LLM 'agents' consumer insurance shopping questions and log what they recommend and cite.

Dry run (default) prints the plan and which personas have credentials. Nothing is sent and nothing costs
money until --execute is given.

    python scripts/run_shopping_agents.py                                 # plan for everything
    python scripts/run_shopping_agents.py --personas anthropic_opus --scenarios home_flood_prone_qld --execute
    python scripts/run_shopping_agents.py --via-openrouter --repeats 3 --execute   # one key for every persona
    python scripts/run_shopping_agents.py --summarise data/agent_runs/<run_id>.jsonl

Credentials come from the environment or a .env file in the project root (see .env.example).
Raw logs go to data/agent_runs/ (gitignored, append-only). A summary CSV is written next to each log.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pds_agents import analysis, config, providers

OUT = ROOT / "data" / "agent_runs"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--personas", default="all", help="comma-separated persona ids, or 'all'")
    p.add_argument("--scenarios", default="all", help="comma-separated scenario ids, or 'all'")
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--via-openrouter", action="store_true", help="route every persona through OpenRouter")
    p.add_argument("--execute", action="store_true", help="actually call the APIs (costs money)")
    p.add_argument("--seed", type=int, default=0, help="seed for the randomised call order")
    p.add_argument("--summarise", type=Path, help="only rebuild the summary CSV for an existing log")
    p.add_argument("--out", type=Path, default=OUT)
    return p.parse_args(argv)


def plan(args: argparse.Namespace) -> tuple[list[tuple], list[str]]:
    personas = config.select(config.load_panel(), args.personas)
    templates, scenarios = config.load_scenarios()
    scenarios = config.select(scenarios, args.scenarios)
    jobs, skipped = [], []
    for persona in personas:
        provider = providers.build(persona, via_openrouter=args.via_openrouter)
        if not provider.available():
            skipped.append(f"{persona['id']} (no {' or '.join(provider.env_keys)})")
            continue
        for scenario in scenarios:
            prompt = config.render(templates, scenario)
            for r in range(args.repeats):
                jobs.append((provider, persona, scenario, prompt, r))
    random.Random(args.seed).shuffle(jobs)  # interleave providers and scenarios to spread time effects
    return jobs, skipped


def write_summary(log: Path) -> Path:
    rows = [analysis.summarise(json.loads(line)) for line in log.read_text().splitlines() if line.strip()]
    out = log.with_suffix(".summary.csv")
    if rows:
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.summarise:
        print("wrote", write_summary(args.summarise)); return 0
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    jobs, skipped = plan(args)
    route = "OpenRouter" if args.via_openrouter else "direct APIs"
    print(f"{len(jobs)} calls planned via {route}"
          f" ({len({j[1]['id'] for j in jobs})} personas x {len({j[2]['id'] for j in jobs})} scenarios"
          f" x {args.repeats} repeats)")
    for s in skipped:
        print("  skipped:", s)
    if not args.execute:
        print("dry run: nothing sent. Add --execute to call the APIs. Web search adds a per-request fee.")
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    log = args.out / f"{run_id}.jsonl"
    with log.open("a") as f:
        for i, (provider, persona, scenario, prompt, r) in enumerate(jobs, 1):
            started = datetime.now(UTC).isoformat()
            result = provider.ask(prompt)
            row = {"run_id": run_id, "started_at": started, "route": route, "scenario": scenario["id"],
                   "product_line": scenario["product_line"], "repeat": r, "prompt": prompt,
                   "prompt_sha": config.prompt_hash(prompt), **asdict(result)}
            f.write(json.dumps(row, default=str) + "\n"); f.flush()
            status = "ERROR " + result.error[:80] if result.error else f"{len(result.citations)} citations"
            print(f"[{i}/{len(jobs)}] {persona['id']:24s} {scenario['id']:26s} {result.latency_s:6.1f}s {status}")
            time.sleep(0.5)
    print("log:", log, "\nsummary:", write_summary(log))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
