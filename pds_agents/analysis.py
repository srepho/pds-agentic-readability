"""Turn an agent's free-text answer and citations into comparable fields: which insurers it named and in
what order, and what kind of sources it relied on (insurer pages, PDS documents, comparison sites ...).

Mention order is a proxy for the recommendation, not a parse of it. Answers that discuss a brand to rule
it out still count as a mention; an LLM-based extractor can replace this later."""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

# brand id -> (name patterns, owned domains). Study brands first, then other brands consumers may be sent to.
BRANDS: dict[str, tuple[list[str], list[str]]] = {
    "nrma": ([r"\bNRMA\b"], ["nrma.com.au"]),
    "cgu": ([r"\bCGU\b"], ["cgu.com.au"]),
    "racv": ([r"\bRACV\b"], ["racv.com.au"]),
    "aami": ([r"\bAAMI\b"], ["aami.com.au"]),
    "gio": ([r"\bGIO\b"], ["gio.com.au"]),
    "suncorp": ([r"\bSuncorp\b"], ["suncorp.com.au"]),
    "apia": ([r"\bApia\b"], ["apia.com.au"]),
    "allianz": ([r"\bAllianz\b"], ["allianz.com.au", "einsure.com.au"]),
    "qbe": ([r"\bQBE\b"], ["qbe.com", "qmdocumentlibrary.qbe.com"]),
    "youi": ([r"\bYoui\b"], ["youi.com.au"]),
    "budget_direct": ([r"\bBudget Direct\b"], ["budgetdirect.com.au"]),
    "coles": ([r"\bColes Insurance\b", r"\bColes (?:car|home|landlord|contents) insurance\b"],
              ["colesinsurance.com.au", "colesinsurance.disconline.com.au"]),
    "racq": ([r"\bRACQ\b"], ["racq.com.au"]),
    "rac_wa": ([r"\bRAC WA\b", r"\bRAC Insurance\b", r"\bRAC(?![A-Za-z])(?= (?:car|home|landlord|insurance))"],
               ["rac.com.au"]),
    "everyday": ([r"\bEveryday Insurance\b", r"\bWoolworths Insurance\b"], ["insurance.everyday.com.au"]),
    "real": ([r"\bReal Insurance\b"], ["realinsurance.com.au"]),
    # not in the study corpus, tracked so recommendations outside it are visible
    "bingle": ([r"\bBingle\b"], ["bingle.com.au"]),
    "ahm": ([r"\bahm\b"], ["ahm.com.au"]),
    "huddle": ([r"\bHuddle\b"], ["huddle.com.au"]),
    "kogan": ([r"\bKogan Insurance\b"], ["koganinsurance.com.au"]),
    "aust_seniors": ([r"\bAustralian Seniors\b"], ["seniors.com.au"]),
    "rac_sa_raa": ([r"\bRAA\b"], ["raa.com.au"]),
    "ract": ([r"\bRACT\b"], ["ract.com.au"]),
    "terri_scheer": ([r"\bTerri Scheer\b"], ["terrischeer.com.au"]),
    "ebm_rentcover": ([r"\bRentCover\b"], ["rentcover.com.au"]),
    "cover_more": ([r"\bCover-?More\b"], ["covermore.com.au"]),
    "fast_cover": ([r"\bFast Cover\b"], ["fastcover.com.au"]),
    "one_cover": ([r"\b1Cover\b"], ["1cover.com.au"]),
    "southern_cross": ([r"\bSouthern Cross Travel\b"], ["scti.com.au"]),
    "medibank": ([r"\bMedibank\b"], ["medibank.com.au"]),
    "bupa": ([r"\bBupa\b"], ["bupa.com.au"]),
    "nib": ([r"\bnib\b"], ["nib.com.au"]),
}
STUDY_BRANDS = list(BRANDS)[:16]
AUTO_GENERAL_DOCS = ["autogeneral.com.au"]  # shared PDS library for Budget Direct and Coles
COMPARATORS = ["canstar.com.au", "finder.com.au", "choice.com.au", "mozo.com.au", "comparethemarket.com.au",
               "iselect.com.au", "ratecity.com.au", "savvy.com.au", "money.com.au", "compareclub.com.au",
               "infochoice.com.au", "productreview.com.au", "canstarblue.com.au", "compare.insure"]
OFFICIAL = ["moneysmart.gov.au", "asic.gov.au", "afca.org.au", "apra.gov.au", "insurancecouncil.com.au",
            "understandinsurance.com.au", "accc.gov.au", "gov.au"]
PDS_HINT = re.compile(r"\.pdf($|\?)|/pds|pds[-_/]|product-disclosure|policy-document|policy-booklet|getpds", re.IGNORECASE)


def _host(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host.removeprefix("www.")


def _matches(host: str, domains: list[str]) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def brand_of_domain(host: str) -> str | None:
    best = None
    for brand, (_, domains) in BRANDS.items():
        for d in domains:  # prefer the most specific domain, e.g. qmdocumentlibrary.qbe.com
            if (host == d or host.endswith("." + d)) and (best is None or len(d) > best[1]):
                best = (brand, len(d))
    if best:
        return best[0]
    return "auto_general" if _matches(host, AUTO_GENERAL_DOCS) else None


def classify_url(url: str) -> dict[str, Any]:
    host = _host(url)
    brand = brand_of_domain(host)
    if brand:
        kind = "insurer"
    elif _matches(host, COMPARATORS):
        kind = "comparator"
    elif _matches(host, OFFICIAL):
        kind = "official"
    elif "reddit.com" in host or "whirlpool" in host:
        kind = "forum"
    else:
        kind = "other"
    is_pds = kind == "insurer" and bool(PDS_HINT.search(url))
    return {"url": url, "host": host, "kind": kind, "brand": brand, "is_pds": is_pds}


def brands_mentioned(text: str) -> list[str]:
    """Brand ids in order of first mention."""
    first: dict[str, int] = {}
    for brand, (patterns, _) in BRANDS.items():
        for pat in patterns:
            m = re.search(pat, text)
            if m and (brand not in first or m.start() < first[brand]):
                first[brand] = m.start()
    return sorted(first, key=first.get)


def summarise(result: dict[str, Any]) -> dict[str, Any]:
    """One flat summary row for a logged AgentResult (as a dict)."""
    cites = [classify_url(c["url"]) for c in result.get("citations") or []]
    mentioned = brands_mentioned(result.get("text") or "")
    kinds = [c["kind"] for c in cites]
    return {
        "run_id": result.get("run_id"), "scenario": result.get("scenario"), "repeat": result.get("repeat"),
        "persona": result.get("persona"), "provider": result.get("provider"), "model": result.get("model"),
        "served_model": result.get("served_model"), "error": bool(result.get("error")),
        "stop_reason": result.get("stop_reason"), "latency_s": result.get("latency_s"),
        "n_words": len((result.get("text") or "").split()),
        "brands_mentioned": ",".join(mentioned), "first_brand": mentioned[0] if mentioned else "",
        "n_study_brands": sum(b in STUDY_BRANDS for b in mentioned),
        "n_searches": len(result.get("search_queries") or []),
        "n_citations": len(cites),
        "n_insurer_citations": kinds.count("insurer"),
        "n_pds_citations": sum(c["is_pds"] for c in cites),
        "n_comparator_citations": kinds.count("comparator"),
        "n_official_citations": kinds.count("official"),
        "cited_insurers": ",".join(sorted({c["brand"] for c in cites if c["brand"]})),
        "cited_hosts": ",".join(sorted({c["host"] for c in cites})),
    }
