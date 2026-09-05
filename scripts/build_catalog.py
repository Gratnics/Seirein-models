#!/usr/bin/env python3
"""
build_catalog.py — Combine every models/<category>/<Provider>/<model>.toml file
into a category-keyed JSON catalog.

Usage:
    python3 scripts/build_catalog.py
    python3 scripts/build_catalog.py --out catalog.json
    python3 scripts/build_catalog.py --models-dir models --out catalog.json

Run this any time after adding, editing, or removing a .toml file under
models/ to regenerate the combined catalog.json. The first directory below
models/ is the modality category (image, embedding, speech-input, or speech)
and the second is the provider. It always rebuilds from scratch.
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


CATEGORIES = ("image", "embedding", "speech-input", "speech")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models-dir",
        default="models",
        help="Directory containing <category>/<Provider>/<model>.toml files (default: models)",
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

    toml_files = sorted(models_dir.glob("**/*.toml"))
    if not toml_files:
        sys.exit(f"error: no .toml files found under {models_dir}")

    catalog = {category: [] for category in CATEGORIES}
    errors = []
    for path in toml_files:
        relative_parts = path.relative_to(models_dir).parts
        if len(relative_parts) != 3:
            errors.append((path, "expected models/<category>/<Provider>/<model>.toml"))
            continue
        category, provider_dir, _ = relative_parts
        if category not in CATEGORIES:
            errors.append((path, f"unknown category '{category}' (expected one of {', '.join(CATEGORIES)})"))
            continue
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            errors.append((path, e))
            continue

        entry = dict(data)  # shallow copy of the TOML entry
        # Cross-check / record the provenance so the JSON is traceable back to its source file,
        # and guard against a mismatched [model].provider inside the TOML itself.
        # POSIX separators on every OS so catalog.json is byte-identical whether built on Windows or in Linux CI.
        entry["_source_file"] = path.relative_to(repo_root).as_posix()
        entry["_category"] = category
        model_provider = entry.get("model", {}).get("provider")
        if model_provider and model_provider != provider_dir:
            errors.append((path, f"folder is '{provider_dir}' but [model].provider is '{model_provider}'"))
        catalog[category].append(entry)

    if errors:
        print(f"Encountered {len(errors)} problem(s) while reading .toml files:", file=sys.stderr)
        for path, e in errors:
            print(f"  - {path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Stable ordering: provider, then model name, within each category.
    for entries in catalog.values():
        entries.sort(key=lambda e: (e.get("model", {}).get("provider", ""), e.get("model", {}).get("name", "")))

    indent = args.indent if args.indent > 0 else None
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=indent, ensure_ascii=False, sort_keys=False)
        f.write("\n")

    providers = sorted({
        e.get("model", {}).get("provider", "?")
        for entries in catalog.values()
        for e in entries
    })
    counts = ", ".join(f"{category}={len(catalog[category])}" for category in CATEGORIES)
    print(f"Wrote {len(toml_files)} models ({counts}) across {len(providers)} providers to {out_path}")


if __name__ == "__main__":
    main()
