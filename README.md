# PDS Agentic Readability

An independent, open research project studying how faithfully AI models reconstruct the coverage
rules in Australian general-insurance **Product Disclosure Statements (PDSs)**, and whether changing
the presentation improves that fidelity.

The first experiment compares the same policy information in three forms: a complete policy bundle,
all relevant original clauses, and a standardised plain-language presentation. This separates overall
extraction performance from the benefit of supplying evidence and the effect of changing its presentation.
See [EXPERIMENT.md](EXPERIMENT.md) for the active v4 protocol.

## What's here

| Path | Purpose |
|---|---|
| `EXPERIMENT.md` | Paired A/B/C pilot design, reference review, scoring and analysis |
| `PLAN.md` | Implementation milestones and expansion gates |
| `data/manifest.yaml` | Source URLs for 16 brands across car / home / landlord / travel; availability varies |
| `data/download_log.csv` | Downloader status log; immutable experiment provenance is still to be implemented |
| `data/metrics_classical.csv` | Provisional classical readability metrics |
| `scripts/find_pdf_links.py` | Harvest PDF links from insurer document-hub pages |
| `scripts/download_pds.py` | Manifest-driven PDF downloader |
| `scripts/extract_text.py` | PyMuPDF extraction into per-PDF text and metadata |
| `scripts/inspect_pdfs.py` | Inspect pages, words and preparation dates |
| `scripts/metrics_classical.py` | Classical formulas plus hedge, negation and cross-reference density |

Downloaded PDFs and extracted text are not committed. Re-create them locally from the manifest;
the source documents remain the property of their respective insurers.

## Reproduce the collection pipeline

```bash
uv sync
source .venv/bin/activate
python -I scripts/download_pds.py
python -I scripts/inspect_pdfs.py
python -I scripts/extract_text.py
python -I scripts/metrics_classical.py
```

Download counts depend on source availability. The local snapshot on 16 October 2026 contains 49 PDFs,
including separate car Part B files. A PDF is not necessarily a complete policy: the experiment will
assemble versioned bundles with all applicable parts and supplements.

## Planned pilot

- Home buildings: eight complete policy bundles and twenty common extraction tasks.
- Three models from different families, tested in fresh sessions across A/B/C presentations.
- Human-verified reference answers and evidence packets, plus independently checked rewrites.
- Primary outcome: correct answers with all material qualifications; primary contrast: standardised
  presentation versus relevant original evidence.
- Per-policy paired charts and error examples, with uncertainty and eligibility reported explicitly.

The pilot measures the selected models' performance. It does not establish human readability, recommend
an insurer, or produce a definitive industry ranking. Earlier experimental designs remain in Git history.

## Status and data limitations

Documents have been collected and first-pass classical metrics computed. The paired experiment, bundle
assembly, checked extraction, annotation and evaluation runner are not yet implemented. No LLM evaluation
has been run, and the final evaluation package has not yet been frozen or preregistered.

The existing text extraction is naive: tables, bullet lists and headings can inflate apparent sentence
length and distort reading order. Treat the classical metrics as provisional; do not quote grade-level
results as validated findings. The v4 study requires extraction QA before evaluation.

Contributions welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

MIT; see [LICENSE](LICENSE). The PDS documents themselves remain the property of their respective insurers.
