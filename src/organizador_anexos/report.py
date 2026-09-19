"""Serialização do relatório auditável."""

from __future__ import annotations

from pathlib import Path
import json

from .organizer import OrganizationResult


def write_report(result: OrganizationResult, path: Path) -> None:
    """Grava o resultado em JSON UTF-8."""
    payload = {
        "mode": result.mode,
        "input": str(result.input_directory),
        "planned_at": result.planned_at.isoformat(),
        "moved_or_planned": result.actions,
        "unmatched": result.unmatched,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
