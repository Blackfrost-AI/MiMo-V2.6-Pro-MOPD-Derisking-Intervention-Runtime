#!/usr/bin/env python3
"""Verify the published runtime package without importing SGLang or PyTorch."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_RELATIVE = Path(
    "artifacts/pro-mopd-prompt32-pass2-lambda2/manifest.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()

    release = json.loads((root / "release-manifest.json").read_text())
    expected = release["overrides"] | release["artifacts"]
    failures: list[str] = []

    for relative, wanted in expected.items():
        path = root / relative
        if not path.is_file():
            failures.append(f"missing: {relative}")
            continue
        actual = sha256(path)
        if actual != wanted:
            failures.append(f"hash mismatch: {relative}: {actual} != {wanted}")

    manifest_path = root / MANIFEST_RELATIVE
    if manifest_path.is_file():
        intervention = json.loads(manifest_path.read_text())
        if intervention.get("schema") != "blackfrost.mimo_mlp_output_intervention.v3":
            failures.append("unexpected intervention schema")
        if intervention.get("source_revision") != release["direction_source"]["revision"]:
            failures.append("direction-source revision mismatch")
        if intervention.get("tested_target_revision") != release["tested_checkpoint"]["revision"]:
            failures.append("tested-target revision mismatch")
        if intervention.get("target_layers") != [46, 47, 48, 49]:
            failures.append("unexpected target layers")
        if intervention.get("router_mutation") is not False:
            failures.append("router mutation must be false")
        if intervention.get("weight_mutation") is not False:
            failures.append("weight mutation must be false")
        for item in intervention.get("directions", []):
            direction_path = manifest_path.parent / item["path"]
            if not direction_path.is_file() or sha256(direction_path) != item["sha256"]:
                failures.append(f"manifest direction mismatch: {item['path']}")

    for relative in release["overrides"]:
        path = root / relative
        if path.is_file():
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeError) as error:
                failures.append(f"compile failure: {relative}: {error}")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print(
        f"OK release={release['release']} files={len(expected)} "
        f"sglang={release['upstream_runtime']['version']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
