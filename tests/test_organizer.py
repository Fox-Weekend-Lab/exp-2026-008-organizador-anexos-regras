from datetime import datetime, timezone
import json
import os

from organizador_anexos.organizer import organize
from organizador_anexos.report import write_report
from organizador_anexos.rules import Rule


def test_simulation_matches_first_rule_and_does_not_change_files(tmp_path):
    source = tmp_path / "invoice.PDF"
    source.write_text("conteúdo", encoding="utf-8")
    report_path = tmp_path / "report.json"
    rules = [
        Rule("pdfs", destination=__import__("pathlib").Path("pdfs"), extension=".pdf"),
        Rule("all", destination=__import__("pathlib").Path("other")),
    ]

    result = organize(tmp_path, rules, report_path, now=datetime(2024, 1, 10, tzinfo=timezone.utc))
    write_report(result, report_path)

    assert source.exists()
    assert not (tmp_path / "pdfs").exists()
    assert result.actions[0]["rule"] == "pdfs"
    assert result.actions[0]["status"] == "planned"
    assert json.loads(report_path.read_text(encoding="utf-8"))["mode"] == "simulation"


def test_execution_resolves_existing_and_planned_collisions(tmp_path):
    from pathlib import Path

    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    destination = tmp_path / "done"
    destination.mkdir()
    (destination / "a.txt").write_text("original", encoding="utf-8")
    rules = [Rule("texts", Path("done"), extension=".txt")]

    result = organize(tmp_path, rules, tmp_path / "report.json", execute=True)

    assert (destination / "a (1).txt").exists()
    assert (destination / "b.txt").exists()
    assert all(action["status"] == "moved" for action in result.actions)


def test_age_prefix_and_report_are_handled_without_scanning_directories(tmp_path):
    from pathlib import Path

    old = tmp_path / "note-old.txt"
    old.write_text("x", encoding="utf-8")
    os.utime(old, (0, 0))
    (tmp_path / "folder").mkdir()
    report = tmp_path / "report.json"
    report.write_text("{}", encoding="utf-8")
    rules = [Rule("old-notes", Path("archive"), prefix="note-", min_age_days=1)]

    result = organize(
        tmp_path,
        rules,
        report,
        now=datetime(2024, 1, 10, tzinfo=timezone.utc),
    )

    assert [item["source"] for item in result.actions] == [str(old)]
    assert result.unmatched == []
