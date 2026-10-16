# PDS Agentic Readability

An independent, open research project studying how faithfully AI models reconstruct the coverage
rules in Australian general-insurance **Product Disclosure Statements (PDSs)**, and whether changing
the presentation improves that fidelity.

The first experiment compares the same policy information in four forms: a complete policy bundle,
all relevant original clauses, those clauses padded back to full-document length with irrelevant text,
and a standardised plain-language presentation. This separates overall extraction performance from the
cost of context length, the cost of finding evidence, and the effect of changing its presentation.
See [EXPERIMENT.md](EXPERIMENT.md) for the active v4 protocol.

## What's here

| Path | Purpose |
|---|---|
| `EXPERIMENT.md` | Paired A/B/B+/C pilot design, reference review, scoring and analysis |
| `EXPERIMENT_OPTIONS.md` | Nine alternative designs for consideration; v4 remains active |
| `PLAN.md` | Implementation milestones and expansion gates |
| `data/manifest.yaml` | Source URLs for 16 brands across car / home / landlord / travel, including supplementary PDSs where published; availability varies |
| `tasks/home_buildings_task_bank_draft.yaml` | Draft 20-task extraction bank for home buildings (12 flagged for the pilot); unreviewed |
| `data/download_log.csv` | Downloader status log; immutable experiment provenance is still to be implemented |
| `data/metrics_classical.csv` | Provisional classical readability metrics |
| `scripts/find_pdf_links.py` | Harvest PDF links from insurer document-hub pages |
| `scripts/download_pds.py` | Manifest-driven downloader for base PDSs, parts and supplements (Chrome TLS impersonation with plain-client fallback) |
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

Download counts depend on source availability. The local snapshot on 16 October 2026 contains 49 base
PDFs, including separate car Part B files, plus 44 supplementary PDSs. A PDF is not necessarily a complete
policy: the experiment will assemble versioned bundles with all applicable parts and supplements, and the
applicability of each supplement to its base PDS version still has to be verified against effective dates.

## Planned pilot

- Home buildings: six complete policy bundles and twelve common extraction tasks, expanding to eight
  and twenty once annotation throughput has been measured.
- Three models from different families, tested in fresh sessions across A/B/B+/C presentations.
- Human-verified reference answers and evidence packets, plus independently checked rewrites whose
  structure is deliberately kept distinct from the response schema.
- Primary outcome: correct answers with all material qualifications; primary contrast: standardised
  presentation versus relevant original evidence. Secondary: confidently-wrong rate and calibration.
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
