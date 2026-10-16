"""Extract text from every PDF in data/raw_pds into data/text/<insurer>/<product>.txt (+ .json metadata).
Keeps page breaks as form-feed markers so later segmentation can use page numbers."""
import json, pathlib, re, sys
import pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, TXT = ROOT / "data" / "raw_pds", ROOT / "data" / "text"

def clean_page(t: str) -> str:
    t = t.replace("­", "")                 # soft hyphens
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)      # de-hyphenate line breaks
    t = re.sub(r"[ \t]+\n", "\n", t)
    return t

def main():
    rows = []
    for pdf in sorted(RAW.rglob("*.pdf")):
        ins, name = pdf.parent.name, pdf.stem
        out = TXT / ins / f"{name}.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        doc = pymupdf.open(pdf)
        pages = [clean_page(p.get_text("text")) for p in doc]
        out.write_text("\f".join(pages))
        words = sum(len(p.split()) for p in pages)
        meta = {"insurer": ins, "product": name, "pages": len(doc), "words": words,
                "chars": sum(len(p) for p in pages), "pdf_metadata": doc.metadata}
        (TXT / ins / f"{name}.json").write_text(json.dumps(meta, indent=1))
        rows.append((ins, name, len(doc), words))
        print(f"{ins:14s} {name:10s} {len(doc):4d}p {words:7d}w")
    print(f"\n{len(rows)} documents extracted")

if __name__ == "__main__":
    main()
