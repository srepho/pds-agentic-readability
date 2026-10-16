# PDS Readability Benchmark — Project Plan

Compare the readability of Product Disclosure Statements (PDS) across major Australian
general insurers and personal-lines products, using (a) classical readability formulas and
(b) a panel of LLMs as judges, then compare the two.

## 1. Scope

**Insurer brands (by group)** — brands within a group often share a document template, so
analyse both at brand level and group level.

| Group | Brands |
|---|---|
| IAG | NRMA, CGU, RACV (IMA JV), Coles (A&G-manufactured, see below) |
| Suncorp | AAMI, GIO, Suncorp, Apia |
| Allianz | Allianz |
| Auto & General | Budget Direct, Coles Insurance |
| Hollard | Real Insurance, Everyday (ex Woolworths) |
| QBE | QBE |
| Youi | Youi |
| Motoring clubs | RACQ (QLD), RAC (WA) |

**Product lines**: Comprehensive Car, Home (building & contents), Landlord, Travel.
Optional later: CTP (state schemes), Pet, Caravan, Motorcycle, Life (different regime).

## 2. Pipeline

```
manifest.yaml --> download_pds.py --> data/raw_pds/<insurer>/<product>.pdf
                                   --> extract_text.py --> data/text/<insurer>/<product>.{md,json}
                                   --> metrics_classical.py --> data/metrics_classical.csv
                                   --> metrics_llm.py       --> data/metrics_llm.csv
                                   --> analysis notebook / report
```

### 2a. Text extraction & segmentation
- PyMuPDF for text; keep page numbers; strip headers/footers/TOC; detect two-column layouts.
- Segment into sections by heading (e.g. "What we cover", "Exclusions", "Making a claim",
  "Definitions") so sections can be compared like-for-like across insurers.
- Record structural stats: pages, words, sentences, tables, defined terms, cross-references.

### 2b. Classical metrics (textstat + custom)
- Flesch Reading Ease, Flesch–Kincaid grade, Gunning Fog, SMOG, Coleman–Liau, ARI, Dale–Chall.
- Avg sentence length, % long sentences (>25 words), % passive voice, % words >3 syllables,
  defined-term density, cross-reference density ("see section..."), negation density
  ("not", "unless", "except"), conditionals ("if", "provided that").
- Lexical: type–token ratio, jargon list hits (insurance-specific wordlist).

### 2c. LLM-as-judge metrics
Models: a Claude model (claude-sonnet-5-5 / claude-opus-5-5), GPT, Gemini — see
`claude-api` skill before wiring up the Anthropic client. Each model scores each section
(and whole doc) on a rubric, e.g. 1–7 scale with written justification:
- Plain-language clarity; Sentence complexity; Jargon/defined-term burden
- Logical structure & navigability; Transparency of exclusions/limits
- "Could a 15-year-old explain what is/isn't covered after reading this?"
Also comprehension probes: give the LLM the section and 5 fixed factual questions
(e.g. "Is flood covered by default?"), measure accuracy — a proxy for findability.
Controls: fixed temperature, same prompt, randomised doc order, repeat 3x for variance,
inter-model agreement (Krippendorff's alpha), and correlation with classical metrics.

### 2d. Analysis & outputs
- League tables by product line and by group; classical vs LLM agreement.
- Section-level heatmaps (which sections are hardest industry-wide).
- Longitudinal option: older PDS versions are still hosted for most brands — can compare
  2018 → 2021 → 2025 to see whether readability has improved (ASIC/plain-language push).
- Report as HTML artifact / notebook.

## 3. Caveats
- PDS length/structure differs (AAMI splits building and contents; RACQ has one Household
  PDS covering owner, landlord and renter; Budget Direct/Coles split car into Part A/B).
- Some PDSs are combined PDS+FSG (travel, Everyday). Normalise by analysing PDS portion.
- Check each file's preparation date; keep `data/download_log.csv` as provenance.
- Copyright: documents are public disclosure documents; fine for internal analysis.
  Don't redistribute the PDFs themselves.
