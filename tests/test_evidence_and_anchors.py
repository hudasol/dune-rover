"""Pin the generated evidence table and the stage 5 anchor results to their committed values."""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


P3 = ("PLN", "TM3", "MOB", "SND", "DUN", "MAP", "ENV", "SCL")   # rows merged through research/phase3/MERGED.txt (SCL added 2026-10-21)


def _p3_expected():
    """Rows in the merged phase 3 files minus the dropped ones (research/phase3/MERGED.txt, dropped.csv)."""
    man = os.path.join(ROOT, "research", "phase3", "MERGED.txt")
    if not os.path.exists(man):
        return 0
    names = [l.strip() for l in open(man, encoding="utf-8") if l.strip() and not l.startswith("#")]
    ids = set()
    for n in names:
        ids |= {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "research", "phase3", n), encoding="utf-8"))}
    dp = os.path.join(ROOT, "research", "phase3", "dropped.csv")
    dropped = {r["id"] for r in csv.DictReader(open(dp, encoding="utf-8"))} if os.path.exists(dp) else set()
    return len(ids - dropped)


def test_evidence_table_has_171_verified_rows_plus_merged_phase3():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "research", "evidence.csv"), encoding="utf-8")))
    old = [r for r in rows if not r["id"].startswith(P3)]
    assert len(old) == 171 and len({r["id"] for r in rows}) == len(rows)
    assert len(rows) - len(old) == _p3_expected()
    assert all(r["verification"].startswith("verified ") for r in rows)
    assert sum(r["verification"].startswith("verified 2026-10-15") for r in rows) == 25
    split = {r["id"]: r for r in rows if r["id"].startswith("FLD-HV13-5")}
    assert set(split) == {"FLD-HV13-5a", "FLD-HV13-5b"}
    assert split["FLD-HV13-5a"]["validation_type"] == "lab" and split["FLD-HV13-5b"]["validation_type"] == "field"
    assert all(r["evidence_label"] == "PUBLISHED" for r in rows)


def test_verification_stats_match_the_log():
    st = json.load(open(os.path.join(ROOT, "research", "verification_stats.json"), encoding="utf-8"))
    assert st["ALL 170 ROWS"]["n"] == 170 and st["ALL 170 ROWS"]["material_error"] == 9
    assert st["supplementary rows from supplied PDFs, phase 3"]["n"] == 26
    n = len(list(csv.DictReader(open(os.path.join(ROOT, "research", "evidence.csv"), encoding="utf-8"))))
    assert st["CURRENT TABLE, latest verdict per row"]["n"] == n == 171 + _p3_expected()
    assert st["CURRENT SUPPLEMENTARY ROWS, latest verdict per row"]["n"] == 27


def test_anchor_summary_is_labelled_and_pinned():
    s = json.load(open(os.path.join(ROOT, "results", "anchors", "summary.json"), encoding="utf-8"))
    assert s["label"].startswith("SIMULATION ONLY")
    assert s["dumont"]["first_line"].startswith("Comparison of unlike vehicles and soils")
    assert abs(s["dumont"]["dumont_cross50_deg"] - 12.59) < 0.01 and abs(s["dumont"]["nominal_cross50_deg"] - 25.46) < 0.01
    assert s["dumont_posthoc_fit"]["label"].startswith("POST HOC")


def test_prediction_tally_counts_every_prediction_row():
    import re, sys
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from tally_predictions import tally
    text = open(os.path.join(ROOT, "docs", "PREDICTIONS.md"), encoding="utf-8").read()
    n_rows = len(re.findall(r"^\| [A-Z]+\d+-\d+ \|", text, flags=re.M))
    assert n_rows >= 60 and sum(sum(c.values()) for c in tally().values()) == n_rows

