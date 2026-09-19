import pytest

from organizador_anexos.rules import RuleValidationError, load_rules


def test_loads_valid_ordered_rules(tmp_path):
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        "rules:\n  - name: imagens\n    destination: imagens\n    extension: .PNG\n",
        encoding="utf-8",
    )

    rules = load_rules(rules_file)

    assert rules[0].name == "imagens"
    assert rules[0].destination.as_posix() == "imagens"
    assert rules[0].extension == ".PNG"


@pytest.mark.parametrize("destination", ["/tmp/destino", "../fora"])
def test_rejects_unsafe_destinations(tmp_path, destination):
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(f"rules:\n  - destination: {destination}\n", encoding="utf-8")

    with pytest.raises(RuleValidationError, match="relativo"):
        load_rules(rules_file)


def test_rejects_missing_destination(tmp_path):
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("rules:\n  - prefix: nota\n", encoding="utf-8")

    with pytest.raises(RuleValidationError, match="destination"):
        load_rules(rules_file)
