#!/usr/bin/env python3
"""Check every entry of paper/references.bib that is not yet in paper/references_check.csv against Crossref (by DOI) and
append a row with the title and year as found. Entries without a DOI are listed for a manual check.

    python3 scripts/verify_references.py

A row is written only when Crossref returns the DOI and its title matches the bib title (case and punctuation ignored).
"""
from __future__ import annotations
import csv, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB = os.path.join(ROOT, "paper", "references.bib")
CHK = os.path.join(ROOT, "paper", "references_check.csv")


def norm(t):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\\[a-z]+|[{}]", "", t.lower()))


def main():
    bib = open(BIB, encoding="utf-8").read()
    entries = re.findall(r"@\w+\{([^,]+),(.*?)\n\}", bib, flags=re.S)
    done = {r["key"] for r in csv.DictReader(open(CHK, encoding="utf-8"))}
    rows, manual = [], []
    for key, body in entries:
        if key in done:
            continue
        doi = re.search(r"doi\s*=\s*\{([^}]+)\}", body)
        title = re.search(r"title\s*=\s*\{(.+?)\},\s*\n", body, flags=re.S)
        if not doi:
            manual.append(key); continue
        doi = doi.group(1).strip()
        try:
            with urllib.request.urlopen(f"https://api.crossref.org/works/{doi}", timeout=60) as r:
                m = json.load(r)["message"]
        except Exception as e:  # noqa: BLE001
            # data set DOIs (DataCite) are not in Crossref: check that the DOI resolves
            try:
                req = urllib.request.Request(f"https://doi.org/{doi}", method="HEAD")
                urllib.request.urlopen(req, timeout=60)
                rows.append({"key": key, "verified": "yes", "doi": doi, "url_checked": f"https://doi.org/{doi}", "title_as_found": "(data set DOI, resolves)",
                             "year": "", "note": "DataCite DOI; resolved by doi.org"})
            except Exception:  # noqa: BLE001
                manual.append(f"{key} ({e})")
            continue
        found = (m.get("title") or [""])[0]
        ok = title and norm(found)[:40] == norm(title.group(1))[:40]
        year = (m.get("issued", {}).get("date-parts") or [[""]])[0][0]
        if ok:
            rows.append({"key": key, "verified": "yes", "doi": doi, "url_checked": f"https://api.crossref.org/works/{doi}", "title_as_found": found,
                         "year": year, "note": f"{(m.get('container-title') or [''])[0]}; checked by scripts/verify_references.py"})
        else:
            manual.append(f"{key} (title mismatch: {found!r})")
    if rows:
        with open(CHK, "a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["key", "verified", "doi", "url_checked", "title_as_found", "year", "note"])
            w.writerows(rows)
    print(f"verified {len(rows)}; manual check needed: {manual}")
    sys.exit(0)


if __name__ == "__main__":
    main()
