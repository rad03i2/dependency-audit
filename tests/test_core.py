import json
from pathlib import Path

from dependency_audit import audit


def test_requirements_detects_unpinned_and_range(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("requests\nflask==3.0.0\nhttpx>=0.27\n", encoding="utf-8")
    report = audit(tmp_path)
    assert report.dependencies == 3
    assert {(f.code, f.package) for f in report.findings} >= {("UNPINNED", "requests"), ("RANGE", "httpx")}
    assert not any(f.package == "flask" and f.code in {"UNPINNED", "RANGE"} for f in report.findings)


def test_node_unbounded_and_missing_lock(tmp_path: Path):
    (tmp_path / "package.json").write_text(json.dumps({"dependencies": {"left-pad": "*", "react": "^19.0.0"}}), encoding="utf-8")
    report = audit(tmp_path)
    codes = {f.code for f in report.findings}
    assert "UNBOUNDED" in codes
    assert "NO_LOCKFILE" in codes
    assert "RANGE" in codes


def test_pyproject_dependencies(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname="x"\ndependencies=["rich==13.9.4"]\n[project.optional-dependencies]\ndev=["pytest>=8"]\n', encoding="utf-8")
    report = audit(tmp_path)
    assert report.dependencies == 2
    assert any(f.package == "pytest" and f.code == "RANGE" for f in report.findings)


def test_conflicting_specs_across_manifests(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[project]\nname="x"\ndependencies=["requests==2.32.0"]\n', encoding="utf-8")
    assert any(f.code == "CONFLICTING_SPEC" for f in audit(tmp_path).findings)


def test_missing_manifest(tmp_path: Path):
    report = audit(tmp_path)
    assert report.counts["error"] == 1
    assert report.findings[0].code == "NO_MANIFEST"
