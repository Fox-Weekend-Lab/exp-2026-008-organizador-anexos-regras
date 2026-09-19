"""Carregamento e validação das regras de organização."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RuleValidationError(ValueError):
    """Indica uma configuração YAML inválida."""


@dataclass(frozen=True)
class Rule:
    name: str
    destination: Path
    extension: str | None = None
    prefix: str | None = None
    min_age_days: float | None = None


def _error(message: str) -> RuleValidationError:
    return RuleValidationError(f"Regras inválidas: {message}")


def _optional_text(value: Any, field: str, position: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise _error(f"a regra {position} deve ter '{field}' como texto não vazio.")
    return value


def _destination(value: Any, position: int) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise _error(f"a regra {position} precisa informar 'destination'.")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise _error(
            f"o destination da regra {position} deve ser relativo e não pode conter '..'."
        )
    return path


def load_rules(path: Path) -> list[Rule]:
    """Lê um YAML e devolve regras ordenadas e validadas."""
    try:
        with path.open("r", encoding="utf-8") as source:
            data = yaml.safe_load(source)
    except FileNotFoundError as exc:
        raise RuleValidationError(f"Arquivo de regras não encontrado: {path}.") from exc
    except OSError as exc:
        raise RuleValidationError(f"Não foi possível ler o arquivo de regras: {exc}.") from exc
    except yaml.YAMLError as exc:
        raise RuleValidationError(f"YAML inválido. Corrija a sintaxe do arquivo: {exc}.") from exc

    if not isinstance(data, dict) or set(data) != {"rules"}:
        raise _error("o arquivo deve conter somente a chave 'rules'.")
    entries = data["rules"]
    if not isinstance(entries, list):
        raise _error("a chave 'rules' deve conter uma lista.")

    allowed = {"name", "destination", "extension", "prefix", "min_age_days"}
    rules: list[Rule] = []
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise _error(f"a regra {position} deve ser um objeto YAML.")
        unknown = set(entry) - allowed
        if unknown:
            raise _error(f"a regra {position} possui chaves não permitidas: {', '.join(sorted(unknown))}.")

        name = _optional_text(entry.get("name"), "name", position) or f"regra-{position}"
        extension = _optional_text(entry.get("extension"), "extension", position)
        prefix = _optional_text(entry.get("prefix"), "prefix", position)
        age = entry.get("min_age_days")
        if age is not None:
            if isinstance(age, bool) or not isinstance(age, (int, float)) or age < 0:
                raise _error(
                    f"a regra {position} deve ter 'min_age_days' numérico e não negativo."
                )
            age = float(age)

        rules.append(
            Rule(
                name=name,
                destination=_destination(entry.get("destination"), position),
                extension=extension,
                prefix=prefix,
                min_age_days=age,
            )
        )
    return rules
