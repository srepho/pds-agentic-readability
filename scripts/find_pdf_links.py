"""Fetch insurer document-hub pages and print every PDF link found (for building the manifest)."""
import re
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "en-AU,en;q=0.9"}

def scan(url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
    except Exception as e:  # noqa: BLE001 - report the page as failed and continue
        return {"url": url, "error": str(e)}
    soup = BeautifulSoup(r.text, "lxml")
    links = {}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if re.search(r"\.pdf(\?|$)", href, re.IGNORECASE) or "pds" in href.lower():
            full = urljoin(url, href)
            text = " ".join(a.get_text(" ", strip=True).split())[:90]
            links.setdefault(full, text)
    # also catch PDF URLs embedded in scripts/JSON
    for m in re.finditer(r"https?://[^\s\"'<>]+?\.pdf", r.text, re.IGNORECASE):
        links.setdefault(m.group(0), "(embedded)")
    return {"url": url, "status": r.status_code, "n": len(links), "links": links}

if __name__ == "__main__":
    out = [scan(u) for u in sys.argv[1:]]
    for o in out:
        print("\n###", o["url"], o.get("status"), o.get("error", ""), "links:", o.get("n"))
        for k, v in sorted(o.get("links", {}).items()):
            print(f"  {v!r:60.60} {k}")
