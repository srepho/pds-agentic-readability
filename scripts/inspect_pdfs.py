"""Quick QA of downloaded PDFs: page count, word count, and any date/version strings on the first 3 pages."""
import pathlib
import re

import fitz  # pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_pds"
DATE = re.compile(r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d\d|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d\d|\b20\d\d\b)", re.IGNORECASE)
PREP = re.compile(r"(prepar\w+|effective|issued?|current as at|date of preparation)[^.\n]{0,60}", re.IGNORECASE)

for pdf in sorted(RAW.rglob("*.pdf")):
    try:
        doc = fitz.open(pdf)
        words = sum(len(p.get_text("words")) for p in doc)
        head = "\n".join(doc[i].get_text() for i in range(min(3, len(doc))))
        prep = [m.group(0).strip() for m in PREP.finditer(head)][:2]
        print(f"{pdf.parent.name:14s} {pdf.name:16s} pages={len(doc):3d} words={words:6d} | {' | '.join(prep)[:110]}")
    except Exception as e:  # noqa: BLE001 - report the unreadable PDF and continue
        print(f"{pdf.parent.name:14s} {pdf.name:16s} ERROR {e}")
