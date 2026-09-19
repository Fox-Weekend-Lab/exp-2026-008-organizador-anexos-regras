"""Regra de negócio para planejar e executar a organização de arquivos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import shutil

from .rules import Rule


@dataclass
class OrganizationResult:
    mode: str
    input_directory: Path
    planned_at: datetime
    actions: list[dict[str, str]]
    unmatched: list[str]


def _matches(path: Path, rule: Rule, now: datetime) -> bool:
    if rule.extension is not None and path.suffix.casefold() != rule.extension.casefold():
        return False
    if rule.prefix is not None and not path.name.startswith(rule.prefix):
        return False
    if rule.min_age_days is not None:
        age_days = max(0.0, now.timestamp() - path.stat().st_mtime) / 86400
        if age_days < rule.min_age_days:
            return False
    return True


def _available_destination(candidate: Path, reserved: set[Path]) -> Path:
    if candidate not in reserved and not candidate.exists():
        return candidate
    index = 1
    while True:
        numbered = candidate.with_name(
            f"{candidate.stem} ({index}){candidate.suffix}"
        )
        if numbered not in reserved and not numbered.exists():
            return numbered
        index += 1


def organize(
    input_directory: Path,
    rules: list[Rule],
    report_path: Path,
    *,
    execute: bool = False,
    now: datetime | None = None,
) -> OrganizationResult:
    """Planeja arquivos e, quando solicitado, move-os para os destinos das regras."""
    input_directory = input_directory.resolve()
    report_path = report_path.resolve()
    current_time = now or datetime.now(timezone.utc)
    reserved: set[Path] = set()
    actions: list[dict[str, str]] = []
    unmatched: list[str] = []

    files = sorted(
        (item for item in input_directory.iterdir() if item.is_file()),
        key=lambda item: item.name,
    )
    for source in files:
        if source.resolve() == report_path:
            continue
        selected = next((rule for rule in rules if _matches(source, rule, current_time)), None)
        if selected is None:
            unmatched.append(str(source))
            continue

        target = _available_destination(input_directory / selected.destination / source.name, reserved)
        reserved.add(target)
        actions.append(
            {
                "source": str(source),
                "destination": str(target),
                "rule": selected.name,
                "status": "planned",
            }
        )

    if execute:
        for action in actions:
            target = Path(action["destination"])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(action["source"], target)
            action["status"] = "moved"

    return OrganizationResult(
        mode="execute" if execute else "simulation",
        input_directory=input_directory,
        planned_at=current_time,
        actions=actions,
        unmatched=unmatched,
    )
