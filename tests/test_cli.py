import json

from organizador_anexos.__main__ import main


def test_cli_simulates_and_writes_report(tmp_path, capsys):
    (tmp_path / "photo.jpg").write_text("image", encoding="utf-8")
    rules = tmp_path / "rules.yaml"
    rules.write_text("rules:\n  - name: fotos\n    destination: fotos\n    extension: .jpg\n", encoding="utf-8")
    report = tmp_path / "report.json"

    code = main(["--input", str(tmp_path), "--rules", str(rules), "--report", str(report)])

    assert code == 0
    assert "simulação" in capsys.readouterr().out
    assert (tmp_path / "photo.jpg").exists()
    assert json.loads(report.read_text(encoding="utf-8"))["moved_or_planned"][0]["status"] == "planned"
