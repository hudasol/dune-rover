"""The one command field day ingest, run on a SYNTHETIC fixture only (tests/fixtures/field_day_synthetic)."""
import csv, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures", "field_day_synthetic")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import ingest_field_day as IFD  # noqa: E402


def test_synthetic_fixture_runs_end_to_end():
    with tempfile.TemporaryDirectory() as td:
        out = IFD.main([FIX, "--label", "synthetic", "--out-root", td])
        for f in ("runs_with_slip.csv", "per_bin.csv", "prediction_scores.csv", "analysis.json", "FIELD_DAY_SUMMARY.md"):
            assert os.path.exists(os.path.join(out, f))
        assert "SYNTHETIC" in open(os.path.join(out, "FIELD_DAY_SUMMARY.md")).read()
        scores = list(csv.DictReader(open(os.path.join(out, "prediction_scores.csv"))))
        assert len(scores) >= 7   # every bin of the 2026-10-15 ladder that has runs is scored
        runs = list(csv.DictReader(open(os.path.join(out, "runs_with_slip.csv"))))
        assert all(r["phi_deg"] == "33.000" for r in runs)   # filled from the station soil tests


def test_synthetic_fixture_never_writes_under_results():
    try:
        IFD.main([FIX, "--label", "synthetic"])
    except SystemExit as e:
        assert "may not write under results" in str(e)
    else:
        raise AssertionError("synthetic fixture was allowed to write under results/")


def test_bad_sheet_is_rejected():
    with tempfile.TemporaryDirectory() as td:
        bad = os.path.join(td, "bad"); shutil.copytree(FIX, bad)
        rows = list(csv.DictReader(open(os.path.join(bad, "runs.csv"))))
        rows[0]["station_id"] = "NOWHERE"; rows[1]["entrapped"] = "maybe"
        with open(os.path.join(bad, "runs.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        sheets, errors, _ = IFD.validate(bad)
        assert any("NOWHERE" in e for e in errors) and any("entrapped" in e for e in errors)
