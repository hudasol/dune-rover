#!/usr/bin/env python3
"""Fail if copyrighted or unlicensed material is committed.

Rules (tracked files, and with --history every blob ever committed):
  1. Any PDF larger than PDF_LIMIT bytes fails.
  2. Any PDF not on the allow list (our own generated PDFs) fails.
  3. Any file larger than FILE_LIMIT bytes fails (except allow-listed figures).
  4. Raw data formats (GeoTIFF, HGT, NetCDF, archives, numpy dumps) fail anywhere.
  5. Anything under a download directory (research/sources, research/verify_sources, data/raw,
     research/phase2 other than .csv and .md) fails, except data/raw/MANIFEST.md.
Exit status 1 on any violation.  No network.  Usage: python3 scripts/check_repo_hygiene.py [--history]
"""
import subprocess, sys, os, fnmatch
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_LIMIT = 3_000_000
FILE_LIMIT = 5_000_000
PDF_ALLOW = {"docs/REPORT.pdf", "docs/EXECUTIVE_BRIEF.pdf", "docs/PROPOSAL_SEED.pdf", "docs/FIELD_DAY_CHECKLIST.pdf"}
RAW_EXT = (".tif", ".tiff", ".hgt", ".nc", ".h5", ".hdf", ".zip", ".tar", ".gz", ".tgz", ".7z", ".npy", ".npz", ".laz", ".las", ".mat")
DOWNLOAD_DIRS = ("research/sources/", "research/verify_sources/", "data/raw/", "research/phase2/")
DIR_OK = {"data/raw/MANIFEST.md"}
def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout
def check(path, size):
    out = []
    low = path.lower()
    if low.endswith(".pdf"):
        if size > PDF_LIMIT: out.append(f"PDF over {PDF_LIMIT} bytes ({size})")
        if path not in PDF_ALLOW: out.append("PDF not on the allow list (source PDFs must not be committed)")
    elif size > FILE_LIMIT and not path.startswith("results/figures/"):
        out.append(f"file over {FILE_LIMIT} bytes ({size})")
    if low.endswith(RAW_EXT): out.append("raw data format")
    for d in DOWNLOAD_DIRS:
        if path.startswith(d) and path not in DIR_OK and not (d == "research/phase2/" and low.endswith((".csv", ".md"))):
            out.append(f"inside download directory {d}")
    return out
def main():
    bad = []
    if "--history" in sys.argv:
        seen = set()
        for line in git("rev-list", "--all", "--objects").splitlines():
            parts = line.split(" ", 1)
            if len(parts) < 2: continue
            sha, path = parts
            info = git("cat-file", "-t", sha).strip()
            if info != "blob": continue
            size = int(git("cat-file", "-s", sha))
            for v in check(path, size):
                if (path, v) not in seen: seen.add((path, v)); bad.append((path, v, "history"))
    else:
        for path in git("ls-files").splitlines():
            if not os.path.exists(os.path.join(ROOT, path)): continue
            for v in check(path, os.path.getsize(os.path.join(ROOT, path))): bad.append((path, v, "tree"))
    for p, v, w in bad: print(f"VIOLATION [{w}] {p}: {v}")
    print("hygiene check:", "FAILED" if bad else "ok")
    sys.exit(1 if bad else 0)
main()
