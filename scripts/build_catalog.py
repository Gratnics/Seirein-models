#!/usr/bin/env python3
"""
build_catalog.py — Combine every models/<Provider>/<model>.toml file into a
single JSON list.

Usage:
    python3 scripts/build_catalog.py
    python3 scripts/build_catalog.py --out catalog.json
    python3 scripts/build_catalog.py --models-dir models --out catalog.json

Run this any time after adding, editing, or removing a .toml file under
models/ to regenerate the combined catalog.json. It always rebuilds from
scratch — it doesn't merge; it derives the JSON entirely from the current
set of .toml files, so deleted/renamed files are reflected automatically.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # fallback for older Python, if installed
    except ModuleNotFoundError:
        sys.exit(
            "error: no TOML parser available. Python 3.11+ (stdlib tomllib) "
            "is required, or install 'tomli' for older Python (pip install tomli)."
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models-dir",
        default="models",
        help="Directory containing <Provider>/<model>.toml files (default: models)",
    )
    parser.add_argument(
        "--out",
        default="catalog.json",
        help="Output JSON file path (default: catalog.json)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation (default: 2; use 0 for compact single-line output)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    models_dir = (repo_root / args.models_dir).resolve()
    out_path = (repo_root / args.out).resolve()

    if not models_dir.is_dir():
        sys.exit(f"error: models directory not found: {models_dir}")

    toml_files = sorted(models_dir.glob("*/*.toml"))
    if not toml_files:
        sys.exit(f"error: no .toml files found under {models_dir}")

    catalog = []
    errors = []
    for path in toml_files:
        provider_dir = path.parent.name
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            errors.append((path, e))
            continue

        entry = dict(data)  # shallow copy: {model:..., resolution:..., input:..., settings:..., output:..., pricing:..., sources:...}
        # Cross-check / record the provenance so the JSON is traceable back to its source file,
        # and guard against a mismatched [model].provider inside the TOML itself.
        # POSIX separators on every OS so catalog.json is byte-identical whether built on Windows or in Linux CI.
        entry["_source_file"] = path.relative_to(repo_root).as_posix()
        model_provider = entry.get("model", {}).get("provider")
        if model_provider and model_provider != provider_dir:
            errors.append((path, f"folder is '{provider_dir}' but [model].provider is '{model_provider}'"))
        catalog.append(entry)

    if errors:
        print(f"Encountered {len(errors)} problem(s) while reading .toml files:", file=sys.stderr)
        for path, e in errors:
            print(f"  - {path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Stable ordering: provider, then model name.
    catalog.sort(key=lambda e: (e.get("model", {}).get("provider", ""), e.get("model", {}).get("name", "")))

    indent = args.indent if args.indent > 0 else None
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=indent, ensure_ascii=False, sort_keys=False)
        f.write("\n")

    providers = sorted({e.get("model", {}).get("provider", "?") for e in catalog})
    print(f"Wrote {len(catalog)} models from {len(toml_files)} files across {len(providers)} providers to {out_path}")


if __name__ == "__main__":
    main()
