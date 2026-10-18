"""Probe insurer sites for 'agent readiness': robots.txt rules for AI crawlers/agents, llms.txt,
Cloudflare-style content signals, and whether a PDS URL can be fetched with different client identities.
Writes data/agent_readiness.csv (one row per insurer) and data/agent_readiness_access.csv (per client).

Caveat: agent user-agent strings are sent from this machine's IP. Sites that verify bots by IP range
will treat these as spoofed, so a block here does not prove the real agent is blocked, and a pass does
not prove the real agent is allowed."""
import csv
import pathlib
import re
import time
import urllib.robotparser
from urllib.parse import urlparse

import requests as plain
import yaml
from curl_cffi import requests as cffi

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITES = {  # insurer -> main site (robots/llms) ; PDS URL comes from the manifest
    "nrma": "https://www.nrma.com.au", "cgu": "https://www.cgu.com.au", "racv": "https://www.racv.com.au",
    "aami": "https://www.aami.com.au", "gio": "https://www.gio.com.au", "suncorp": "https://www.suncorp.com.au",
    "apia": "https://www.apia.com.au", "allianz": "https://www.allianz.com.au", "qbe": "https://www.qbe.com",
    "youi": "https://www.youi.com.au", "budget_direct": "https://www.budgetdirect.com.au",
    "coles": "https://www.colesinsurance.com.au", "racq": "https://www.racq.com.au", "rac_wa": "https://rac.com.au",
    "everyday": "https://insurance.everyday.com.au", "real": "https://www.realinsurance.com.au",
}
AI_AGENTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
             "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot", "meta-externalagent"]
CHROME = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
CLIENTS = {
    "python_default": None,
    "chrome_ua": CHROME,
    "ChatGPT-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
    "Claude-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-User/1.0; +Claude-User@anthropic.com)",
    "Perplexity-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)",
    "chrome_impersonated": "IMPERSONATE",
}

def get(url, ua):
    try:
        if ua == "IMPERSONATE":
            r = cffi.get(url, impersonate="chrome", timeout=40, allow_redirects=True)
        else:
            r = plain.get(url, headers={"User-Agent": ua} if ua else None, timeout=40, allow_redirects=True)
        return r.status_code, r.headers.get("content-type", ""), r.content
    except Exception as e:  # noqa: BLE001 - a probe records any network failure as a result
        return "ERR", type(e).__name__, b""

def robots_summary(base):
    code, ct, body = get(base + "/robots.txt", "IMPERSONATE")
    text = body.decode("utf-8", "replace") if code == 200 and "html" not in ct.lower() else ""
    rp = urllib.robotparser.RobotFileParser(); rp.parse(text.splitlines())
    named = {a for a in AI_AGENTS if re.search(rf"(?im)^\s*user-agent:\s*{re.escape(a)}\s*$", text)}
    return code, text, rp, named

def main():
    man = yaml.safe_load((ROOT / "data/manifest.yaml").read_text())["insurers"]
    rows, access = [], []
    for ins, base in SITES.items():
        prods = man[ins].get("products") or {}
        pds = (prods.get("home") or prods.get("car") or {}).get("url", "")
        code, text, rp, named = robots_summary(base)
        blocked_site = [a for a in AI_AGENTS if text and not rp.can_fetch(a, base + "/")]
        blocked_pds = [a for a in AI_AGENTS if text and pds and urlparse(pds).netloc == urlparse(base).netloc
                       and not rp.can_fetch(a, pds)]
        signal = "; ".join(sorted(set(re.findall(r"(?im)^\s*content-signal:\s*(.+)$", text))))[:120]
        llms = {}
        for f in ("llms.txt", "llms-full.txt"):
            c, ct, b = get(f"{base}/{f}", "IMPERSONATE")
            llms[f] = c == 200 and "html" not in ct.lower() and len(b) > 50
        per_client = {}
        if pds:
            for name, ua in CLIENTS.items():
                c, ct, b = get(pds, ua)
                ok = c == 200 and b[:5] == b"%PDF-"
                per_client[name] = "PDF" if ok else str(c)
                access.append([ins, name, pds, c, ct[:40], ok]); time.sleep(0.7)
        rows.append({
            "insurer": ins, "site": base, "robots_txt": code,
            "ai_agents_named": len(named), "ai_agents_blocked_sitewide": ",".join(blocked_site) or "-",
            "ai_agents_blocked_on_pds_path": ",".join(blocked_pds) or "-",
            "content_signal": signal or "-", "llms_txt": llms["llms.txt"], "llms_full_txt": llms["llms-full.txt"],
            "pds_host": urlparse(pds).netloc if pds else "-", **{f"fetch_{k}": v for k, v in per_client.items()},
        })
        print(ins, code, "named", len(named), "blocked", len(blocked_site), "llms", llms["llms.txt"], per_client)
    with open(ROOT / "data/agent_readiness.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(ROOT / "data/agent_readiness_access.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["insurer", "client", "url", "status", "content_type", "got_pdf"]); w.writerows(access)

if __name__ == "__main__":
    main()
