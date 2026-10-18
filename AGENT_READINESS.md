# Agent readiness of insurer websites

Can an AI agent acting for a consumer actually reach an insurer's PDS? Probed 16 and 18 October 2026 with
`scripts/probe_agent_readiness.py`; raw results in `data/agent_readiness.csv` and
`data/agent_readiness_access.csv`.

## Summary table

| Insurer | Group | robots.txt stance on AI agents | llms.txt | PDS fetch as AI agent¹ | PDS fetch as plain script | PDS fetch as browser | Docs page discoverable by agent | Verdict |
|---|---|---|---|---|---|---|---|---|
| Everyday | Hollard | Allow all, no AI rules | ✅ Detailed, links PDS pages | ✅ | ✅ | ✅ | ✅ | **Agent-ready** |
| Allianz | Allianz | Allow all, no AI rules | ✅ Detailed, no PDS links | ✅ | ✅ | ✅ | ✅ (PDFs on einsure.com.au) | **Open + signposted** |
| RACV | IAG (IMA) | Allow all, no AI rules | ❌ | ✅ | ✅ | ✅ | ✅ | Open |
| AAMI | Suncorp | Allow all, no AI rules | ❌ | ✅ | ✅ | ✅ | ✅ | Open |
| GIO | Suncorp | Allow all, no AI rules | ❌ | ✅ | ✅ | ✅ | ✅ | Open |
| Suncorp | Suncorp | Allow all, no AI rules | ❌ | ✅ | ✅ | ✅ | ✅ | Open |
| Apia | Suncorp | Allow all, no AI rules | ❌ | ✅ | ✅ | ✅ | ✅ | Open |
| Youi | Youi | Allow all, no AI rules | ❌ | ✅ | ✅ | ✅ | ⚠️ PDS served via redirect endpoints | Open |
| RACQ | RACQ | Allow all, no AI rules | ❌ | ✅ | ✅ | ✅² | ✅ | Open |
| RAC WA | RAC | Allow all, no AI rules | ❌ | ✅ | ✅ | ✅ | ⚠️ Hub page JS-rendered; product sub-pages fine | Open |
| QBE | QBE | Allow all, no AI rules | ⚠️ Group-level only, no AU or PDS content | ✅ | ❌ 403 | ✅ | ❌ AU policy-document pages return 403 to scripted clients, including a real agent fetch tool³ | **Blocked at discovery** |
| NRMA | IAG | Allow all, no AI rules | ❌ | ❌ 403 | ❌ 403 | ✅ | ✅ | **Says yes, blocks by user agent** |
| CGU | IAG | Allow all, no AI rules | ❌ | ❌ 403 | ❌ 403 | ✅ | ✅ | **Says yes, blocks by user agent** |
| Budget Direct | Auto & General | Allow all except named ad bots | ❌ | ❌ 403 | ❌ 403 | ❌ 403 with browser UA; ✅ only with full browser TLS fingerprint | ✅ (via autogeneral.com.au) | **Hostile to agents** |
| Coles Insurance | Auto & General | No robots.txt served: bot-challenge page instead | ❌ | ❌ 403 | ❌ 403 | ❌ 403 with browser UA; ✅ only with full browser TLS fingerprint | ✅ (via autogeneral.com.au) | **Hostile to agents** |
| Real Insurance | Hollard | Unavailable | ❌ | ❌ 503 | ❌ 503 | ❌ 503 | ❌ | **Down** (every client, 16 and 18 Oct) |

¹ ChatGPT-User, Claude-User and Perplexity-User user-agent strings; all three gave identical results at every site.
² RACQ's server rejects the impersonated-browser TLS handshake but serves real browsers and every plain client.
³ Claude Code's WebFetch tool received HTTP 403 on all three QBE policy-document pages during document collection.

## Findings

- **No insurer names an AI agent in robots.txt.** Every readable file is a generic `User-agent: *` group, and none carries content-signal directives. Policy intent towards agents is unstated everywhere.
- **Three insurers publish llms.txt.** Only Everyday's points agents towards PDS pages. Allianz's is detailed but product-marketing focused. QBE's is a global group file with no Australian content.
- **Stated policy and enforced policy diverge.** NRMA and CGU allow everything in robots.txt yet return 403 to agent user agents while serving the same file to a browser user agent. Budget Direct and Coles go further: their bot manager blocks anything without a genuine browser TLS fingerprint, so only browser-driving agents get through.
- **The blocking tracks underwriting groups.** Every Suncorp brand is open. Both IAG direct brands block by user agent, while RACV, which IAG issues through a joint venture on its own site, is open. Both Auto & General brands are hostile.
- **QBE fails at discovery, not retrieval.** Its PDFs on `qmdocumentlibrary.qbe.com` are fetchable by anyone, but the links are only exposed on pages that refuse scripted clients. An agent with a URL succeeds. An agent that has to find the URL fails.

## Caveats

- Agent user-agent strings were sent from a residential IP. Sites that verify bots by published IP ranges will treat them as spoofed. A block here does not prove the real agent is blocked, and a pass does not prove it is allowed. Testing from real agent products is a proposed experiment, see `EXPERIMENTS_OVERVIEW.md`.
- One PDS URL per insurer was tested, normally home. Document hosts can differ from the main site (Allianz uses einsure.com.au, Budget Direct uses secure.budgetdirect.com.au), and the main-site robots.txt does not govern them.
- Bot-management rules change often. Treat this as a dated snapshot and re-run the probe before quoting it.
