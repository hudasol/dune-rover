#!/usr/bin/env python3
"""Regex secrets scan over tracked files and (with --history) every added line in git history.

Not a replacement for gitleaks or GitHub secret scanning; it catches the common token shapes.
Prints file and pattern name, never the secret itself.  Exit 1 if anything matches.
"""
import re, subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERNS = {
 "github token": r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b",
 "aws access key id": r"\bAKIA[0-9A-Z]{16}\b",
 "aws secret": r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}",
 "private key block": r"-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY",
 "slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}",
 "google api key": r"\bAIza[0-9A-Za-z_\-]{35}\b",
 "anthropic or openai key": r"\bsk-(ant-)?[A-Za-z0-9_\-]{32,}\b",
 "bearer token": r"(?i)\bauthorization:\s*bearer\s+[A-Za-z0-9._\-]{20,}",
 "generic assignment": r"(?i)\b(api[_-]?key|secret|passwd|password|token)\b\s*[:=]\s*['\"][A-Za-z0-9/+_\-]{16,}['\"]",
 "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
}
RX = {k: re.compile(v) for k, v in PATTERNS.items()}
SELF = "scripts/scan_secrets.py"
def hits(text):
    return sorted({k for k, rx in RX.items() if rx.search(text)})
def main():
    found = []
    ls = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    for p in ls:
        if p == SELF or p.endswith((".png", ".pdf", ".tif", ".jpg")): continue
        try: t = open(os.path.join(ROOT, p), encoding="utf-8", errors="ignore").read()
        except OSError: continue
        for h in hits(t): found.append((p, h, "tree"))
    if "--history" in sys.argv:
        log = subprocess.run(["git", "log", "--all", "-p", "--no-color", "--text", "--format=commit %H"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8", "ignore")
        cur, f = "", None
        for line in log.splitlines():
            if line.startswith("commit "): cur = line[7:19]; continue
            if line.startswith("+++ b/"): f = line[6:]; continue
            if line.startswith("+") and not line.startswith("+++") and f != SELF:
                for h in hits(line): found.append((f"{f}@{cur}", h, "history"))
    seen = set()
    for p, h, w in found:
        if (p, h) not in seen: seen.add((p, h)); print(f"POSSIBLE SECRET [{w}] {p}: {h}")
    print("secrets scan:", "FOUND" if seen else "clean", f"({len(ls)} tracked files" + (", full history" if "--history" in sys.argv else "") + ")")
    sys.exit(1 if seen else 0)
main()
