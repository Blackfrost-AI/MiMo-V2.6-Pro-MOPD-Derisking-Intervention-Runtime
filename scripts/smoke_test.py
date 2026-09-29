#!/usr/bin/env python3
"""Small OpenAI-compatible API smoke test for the packaged runtime."""

from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


def get_json(url: str, timeout: float) -> dict:
    with urlopen(url, timeout=timeout) as response:
        return json.load(response)


def post_json(url: str, payload: dict, timeout: float) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:30000/v1")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    models = get_json(f"{base}/models", args.timeout).get("data", [])
    if not models:
        raise SystemExit("no served model returned by /models")
    model = args.model or models[0]["id"]
    result = post_json(
        f"{base}/chat/completions",
        {
            "model": model,
            "messages": [{"role": "user", "content": "Reply with exactly: MOPD RUNTIME READY"}],
            "temperature": 0,
            "max_tokens": 64,
        },
        args.timeout,
    )
    choice = result.get("choices", [{}])[0]
    content = choice.get("message", {}).get("content", "").strip()
    if content != "MOPD RUNTIME READY" or choice.get("finish_reason") != "stop":
        raise SystemExit(f"unexpected completion: {json.dumps(result)}")
    print(json.dumps({"ok": True, "model": model, "usage": result.get("usage")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
