"""The hygiene and secrets scripts must actually fail on bad input (tested in a throwaway git repo)."""
import os, subprocess, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(script, cwd, *args):
    # scripts locate the repo from their own path, so copy them next to a scratch repo
    d = os.path.join(cwd, "scripts"); os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(ROOT, "scripts", script), d)
    return subprocess.run([sys.executable, os.path.join(d, script), *args], cwd=cwd, capture_output=True, text=True)
def repo(tmp_path):
    for c in (["init", "-q"], ["config", "user.email", "t@example.org"], ["config", "user.name", "t"]):
        subprocess.run(["git", *c], cwd=tmp_path, check=True)
def commit(tmp_path):
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "x"], cwd=tmp_path, check=True)
def test_clean_repo_passes(tmp_path):
    repo(tmp_path); (tmp_path / "a.txt").write_text("hello"); commit(tmp_path)
    assert run("check_repo_hygiene.py", tmp_path).returncode == 0
def test_source_pdf_fails(tmp_path):
    repo(tmp_path); (tmp_path / "paper.pdf").write_bytes(b"%PDF-1.4 small"); commit(tmp_path)
    r = run("check_repo_hygiene.py", tmp_path); assert r.returncode == 1 and "allow list" in r.stdout
def test_big_pdf_fails(tmp_path):
    repo(tmp_path); (tmp_path / "docs").mkdir(); (tmp_path / "docs/REPORT.pdf").write_bytes(b"0" * 3_100_000); commit(tmp_path)
    r = run("check_repo_hygiene.py", tmp_path); assert r.returncode == 1 and "over" in r.stdout
def test_raw_dem_fails(tmp_path):
    repo(tmp_path); (tmp_path / "data/raw").mkdir(parents=True); (tmp_path / "data/raw/tile.tif").write_bytes(b"II*"); commit(tmp_path)
    assert run("check_repo_hygiene.py", tmp_path).returncode == 1
def test_history_catches_deleted_pdf(tmp_path):
    repo(tmp_path); (tmp_path / "p.pdf").write_bytes(b"%PDF"); commit(tmp_path)
    os.remove(tmp_path / "p.pdf"); commit(tmp_path)
    assert run("check_repo_hygiene.py", tmp_path).returncode == 0
    assert run("check_repo_hygiene.py", tmp_path, "--history").returncode == 1
def test_secret_detected_not_printed(tmp_path):
    repo(tmp_path); tok = "ghp_" + "a1B2c3D4e5" * 4
    (tmp_path / "x.py").write_text(f'T = "{tok}"\n'); commit(tmp_path)
    r = run("scan_secrets.py", tmp_path)
    assert r.returncode == 1 and "github token" in r.stdout and tok not in r.stdout
def test_clean_secrets(tmp_path):
    repo(tmp_path); (tmp_path / "x.py").write_text("x = 1\n"); commit(tmp_path)
    assert run("scan_secrets.py", tmp_path, "--history").returncode == 0
