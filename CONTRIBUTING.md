# Contributing

Issues and pull requests are welcome.

- **Adding an insurer or product**: add an entry to `data/manifest.yaml` pointing at the current PDS URL on the
  insurer's own site, then run `python -I scripts/download_pds.py` and `python -I scripts/inspect_pdfs.py` and
  include the inspector output in your PR.
- **Running the pipeline**: see README. Please do not commit downloaded PDFs or extracted text; they are
  re-created from the manifest.
- **Code style**: `ruff check` clean, type hints where practical.
- **Conduct**: be kind and constructive. Harassment of any kind is not tolerated.
