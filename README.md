# PDS Agentic Readability

An independent, open benchmark of how readable Australian general-insurance **Product Disclosure Statements (PDSs)**
are: for people, using classical readability formulas, and for **AI agents**, by measuring how faithfully a
range of LLMs can extract and compare the coverage a PDS actually describes.

Why agents? Consumers increasingly ask an AI assistant to "find me the best cover". That agent has to read
the PDS. A PDS that models misread is a PDS that will be misrepresented to customers.

## What's here

| Path | Purpose |
|---|---|
| `PLAN.md` | Project scope, pipeline and caveats |
| `EXPERIMENT.md` | Experimental design, v1 (rubric/pairwise) to v3 (agentic extraction), hypotheses, model panel |
| `data/manifest.yaml` | Insurer x product -> current PDS URL (16 brands, car / home / landlord / travel) |
| `data/download_log.csv` | Provenance of every downloaded file |
| `data/metrics_classical.csv` | First-pass classical readability metrics (see caveat below) |
| `scripts/find_pdf_links.py` | Harvest PDF links from insurer document-hub pages |
| `scripts/download_pds.py` | Manifest-driven downloader (uses Chrome TLS impersonation; several insurer hosts block plain clients) |
| `scripts/extract_text.py` | PyMuPDF text extraction to `data/text/` |
| `scripts/inspect_pdfs.py` | QA: pages, words, preparation date per PDF |
| `scripts/metrics_classical.py` | Flesch, Fog, SMOG, Dale-Chall plus hedge / negation / cross-reference density |

Downloaded PDFs and extracted text are **not** committed. They are public disclosure documents, but they are
large and the insurers own them; re-create them locally from the manifest.

## Quick start

```bash
uv sync
source .venv/bin/activate
python -I scripts/download_pds.py      # ~47 PDFs into data/raw_pds/
python -I scripts/inspect_pdfs.py      # check dates and page counts
python -I scripts/extract_text.py      # -> data/text/
python -I scripts/metrics_classical.py # -> data/metrics_classical.csv
```

## Coverage (Oct 2026)

Brands: NRMA, CGU, RACV, AAMI, GIO, Suncorp, Apia, Allianz, QBE, Youi, Budget Direct, Coles, RACQ, RAC WA,
Everyday (ex Woolworths), Real Insurance. Product lines: comprehensive car, home and contents, landlord, travel
where offered. See `data/manifest.yaml` for the exact documents and versions.

## Caveat on the first-pass metrics

`metrics_classical.csv` is computed on naive text extraction. Tables, bullet lists and headings without full
stops inflate sentence length, so the grade-level figures are directional only. Layout-aware extraction and
section segmentation are the next step before any results should be quoted.

## Status

Early. Documents collected, classical metrics drafted, experimental design written. LLM judging not yet run.
Contributions welcome, see `CONTRIBUTING.md`.

## Licence

MIT. See `LICENSE`. The PDS documents themselves remain the property of their respective insurers.
