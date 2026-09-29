#!/usr/bin/env python3
"""Create a private SGLang overlay and apply the qualified MiMo overrides."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SGLANG = "0.5.19"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "runtime-overlay")
    parser.add_argument(
        "--base-package",
        type=Path,
        help="Path to a pristine sglang package directory; defaults to the installed package",
    )
    args = parser.parse_args()

    if args.base_package is None:
        version = importlib.metadata.version("sglang")
        if version != REQUIRED_SGLANG:
            raise SystemExit(f"sglang=={REQUIRED_SGLANG} required; found {version}")
        spec = importlib.util.find_spec("sglang")
        if spec is None or not spec.submodule_search_locations:
            raise SystemExit("cannot locate the installed sglang package")
        source = Path(next(iter(spec.submodule_search_locations))).resolve()
    else:
        version = REQUIRED_SGLANG
        source = args.base_package.expanduser().resolve()
        if not (source / "__init__.py").is_file():
            raise SystemExit(f"not an sglang package directory: {source}")
    output = args.output.expanduser().resolve()
    target = output / "sglang"
    if output.exists():
        raise SystemExit(f"output already exists; choose a new path: {output}")

    release = json.loads((ROOT / "release-manifest.json").read_text())
    for relative, wanted in release["upstream_base_sha256"].items():
        path = source / relative.removeprefix("sglang/")
        if not path.is_file() or sha256(path) != wanted:
            raise SystemExit(f"pristine SGLang base verification failed: {relative}")
    for relative, wanted in release["overrides"].items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != wanted:
            raise SystemExit(f"override verification failed: {relative}")

    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    for relative in release["overrides"]:
        override = ROOT / relative
        destination = output / relative.removeprefix("overrides/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(override, destination)

    provenance = {
        "schema": "blackfrost.mimo_runtime_overlay.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "base_sglang": version,
        "base_package": str(source),
        "release": release["release"],
        "overrides": release["overrides"],
    }
    (output / "blackfrost-overlay.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
