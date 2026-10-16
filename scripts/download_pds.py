"""Download every PDS in data/manifest.yaml into data/raw_pds/<insurer>/<product>.pdf and write a CSV log."""
import csv, sys, time, pathlib, hashlib
import yaml
import requests as plain_requests
from curl_cffi import requests  # Chrome TLS impersonation: several insurer WAFs block plain python/curl

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_pds"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
      "Accept": "application/pdf,*/*;q=0.8", "Accept-Language": "en-AU,en;q=0.9"}

def fetch(url, dest):
    try:
        r = requests.get(url, headers=UA, timeout=90, allow_redirects=True, impersonate="chrome")
    except Exception:
        # a few hosts (e.g. racq.com.au) fail TLS under impersonation but accept a plain client
        r = plain_requests.get(url, headers=UA, timeout=90, allow_redirects=True)
    ct = r.headers.get("content-type", "")
    ok = r.status_code == 200 and (r.content[:5] == b"%PDF-")
    if ok:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
    return ok, r.status_code, ct, len(r.content)

def main():
    man = yaml.safe_load((ROOT / "data" / "manifest.yaml").read_text())
    rows = []
    for ins, meta in man["insurers"].items():
        for prod, spec in (meta.get("products") or {}).items():
            urls = [spec["url"]] + list(spec.get("parts", []))
            names = [f"{prod}.pdf"] + [f"{prod}_part{i+2}.pdf" for i in range(len(spec.get("parts", [])))]
            for j, sup in enumerate(spec.get("supplements", []), start=1):
                urls.append(sup["url"]); names.append(f"{prod}_spds{j}.pdf")
            for url, fname in zip(urls, names):
                dest = RAW / ins / fname
                if dest.exists():
                    rows.append([ins, prod, fname, url, "cached", "", dest.stat().st_size]); continue
                try:
                    ok, code, ct, n = fetch(url, dest)
                except Exception as e:
                    ok, code, ct, n = False, "ERR", str(e)[:80], 0
                rows.append([ins, prod, fname, url, "ok" if ok else "FAIL", f"{code} {ct}", n])
                print(f"{'OK  ' if ok else 'FAIL'} {ins:14s} {fname:16s} {code} {ct[:30]} {n//1024}KB")
                time.sleep(1.0)
    with open(ROOT / "data" / "download_log.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["insurer", "product", "file", "url", "status", "http", "bytes"]); w.writerows(rows)

if __name__ == "__main__":
    main()
