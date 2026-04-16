#!/usr/bin/env python3
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ENTRY_SCHEMA_PATH = ROOT / "control/unchained/schemas/entry.schema.json"
ENTRIES_ROOT = ROOT / "data/entries"
DICT_LANGUAGES = ROOT / "data/dictionary/languages.json"
DICT_STYLES = ROOT / "data/dictionary/styles.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    schema = load_json(ENTRY_SCHEMA_PATH)
    validator = Draft202012Validator(schema)

    langs = load_json(DICT_LANGUAGES)
    styles = load_json(DICT_STYLES)
    allowed_languages = set(langs["languages"])
    allowed_mix_modes = set(langs["mix_modes"])
    allowed_styles = set(styles["styles"])

    errors = []

    for path in sorted(ENTRIES_ROOT.rglob("*.json")):
        payload = load_json(path)
        for err in validator.iter_errors(payload):
            errors.append(f"{path}: {err.message}")

        for language in payload.get("languages", []):
            if language not in allowed_languages:
                errors.append(f"{path}: unknown language '{language}'")

        mix_mode = payload.get("mix_mode")
        if mix_mode and mix_mode not in allowed_mix_modes:
            errors.append(f"{path}: unknown mix_mode '{mix_mode}'")

        style = payload.get("style")
        if style and style not in allowed_styles:
            errors.append(f"{path}: unknown style '{style}'")

    if errors:
        print("control-entry validation failed")
        for err in errors:
            print(f" - {err}")
        return 1

    print("control-entry validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
