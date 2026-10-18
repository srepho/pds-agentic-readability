"""Compute classical readability metrics for every extracted text -> data/metrics_classical.csv"""
import csv
import pathlib
import re

import textstat

ROOT = pathlib.Path(__file__).resolve().parents[1]
TXT = ROOT / "data" / "text"
HEDGES = re.compile(r"\b(unless|except|provided that|subject to|notwithstanding|other than|only if)\b", re.IGNORECASE)
NEG = re.compile(r"\b(not|no|never|neither|nor|cannot|won't|don't|isn't|aren't)\b", re.IGNORECASE)
XREF = re.compile(r"\b(see|refer to|as described in|set out in|under the heading|section|page)\s+['\"“]?[A-Z0-9]", re.IGNORECASE)

def sentences(text):
    text = re.sub(r"\s+", " ", text)
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text) if len(s.split()) >= 3]

def metrics(text):
    sents = sentences(text)
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", text)
    nw = max(len(words), 1)
    long_s = sum(1 for s in sents if len(s.split()) > 25)
    return {
        "words": nw, "sentences": len(sents),
        "avg_sentence_len": round(nw / max(len(sents), 1), 1),
        "pct_long_sentences": round(100 * long_s / max(len(sents), 1), 1),
        "flesch_reading_ease": round(textstat.flesch_reading_ease(text), 1),
        "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(text), 1),
        "gunning_fog": round(textstat.gunning_fog(text), 1),
        "smog": round(textstat.smog_index(text), 1),
        "coleman_liau": round(textstat.coleman_liau_index(text), 1),
        "ari": round(textstat.automated_readability_index(text), 1),
        "dale_chall": round(textstat.dale_chall_readability_score(text), 1),
        "pct_polysyllables": round(100 * textstat.polysyllabcount(text) / nw, 1),
        "hedges_per_1k": round(1000 * len(HEDGES.findall(text)) / nw, 1),
        "negations_per_1k": round(1000 * len(NEG.findall(text)) / nw, 1),
        "xrefs_per_1k": round(1000 * len(XREF.findall(text)) / nw, 1),
        "type_token_ratio": round(len({w.lower() for w in words}) / nw, 3),
    }

def main():
    rows = []
    for txt in sorted(TXT.rglob("*.txt")):
        text = txt.read_text().replace("\f", "\n")
        rows.append({"insurer": txt.parent.name, "product": txt.stem, **metrics(text)})
    out = ROOT / "data" / "metrics_classical.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
