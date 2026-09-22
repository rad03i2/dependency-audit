import json
from pathlib import Path

from dependency_audit.cli import main


def test_cli_json_and_threshold(tmp_path: Path, capsys):
    (tmp_path / "requirements.txt").write_text("requests\n", encoding="utf-8")
    assert main([str(tmp_path), "--json", "--fail-on", "warning"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["dependencies"] == 1
    assert payload["counts"]["warning"] == 1


def test_cli_never_fails(tmp_path: Path):
    assert main([str(tmp_path), "--fail-on", "never"]) == 0
