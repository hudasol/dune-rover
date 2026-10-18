"""Pin the generated evidence table and the stage 5 anchor results to their committed values."""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_evidence_table_has_171_verified_rows():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "research", "evidence.csv"), encoding="utf-8")))
    assert len(rows) == 171 and len({r["id"] for r in rows}) == 171
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
    assert st["CURRENT TABLE, latest verdict per row"]["n"] == 171
    assert st["CURRENT SUPPLEMENTARY ROWS, latest verdict per row"]["n"] == 27


def test_anchor_summary_is_labelled_and_pinned():
    s = json.load(open(os.path.join(ROOT, "results", "anchors", "summary.json"), encoding="utf-8"))
    assert s["label"].startswith("SIMULATION ONLY")
    assert s["dumont"]["first_line"].startswith("Comparison of unlike vehicles and soils")
    assert abs(s["dumont"]["dumont_cross50_deg"] - 12.59) < 0.01 and abs(s["dumont"]["nominal_cross50_deg"] - 25.46) < 0.01
    assert s["dumont_posthoc_fit"]["label"].startswith("POST HOC")
