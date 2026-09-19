"""Interface de linha de comando do organizador."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .organizer import organize
from .report import write_report
from .rules import RuleValidationError, load_rules


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Organiza anexos conforme regras YAML.")
    parser.add_argument("--input", help="Pasta de entrada a ser organizada.")
    parser.add_argument("--rules", help="Arquivo YAML com as regras.")
    parser.add_argument("--report", help="Caminho do relatório JSON.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Move os arquivos. Sem esta opção, apenas simula.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    missing = [name for name in ("input", "rules", "report") if getattr(args, name) is None]
    if missing:
        print(f"Erro: informe {' ,'.join('--' + item for item in missing)} para continuar.", file=sys.stderr)
        return 2

    input_directory = Path(args.input)
    if not input_directory.is_dir():
        print("Erro: --input deve indicar uma pasta existente.", file=sys.stderr)
        return 2

    try:
        rules = load_rules(Path(args.rules))
        result = organize(input_directory, rules, Path(args.report), execute=args.execute)
        write_report(result, Path(args.report))
    except (RuleValidationError, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    action_word = "movidos" if args.execute else "planejados em simulação"
    print(
        f"Concluído: {len(result.actions)} arquivo(s) {action_word}; "
        f"{len(result.unmatched)} sem regra. Relatório: {args.report}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
