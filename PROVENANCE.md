# Provenance

## Runtime base

- Project: SGLang
- Release: `0.5.19`
- Upstream commit: `0bcd822377da7b5718e674eaf9c870d349424dd1`
- Official CPython 3.12 wheel SHA-256:
  - x86-64: `fdc65d1235f6861ad3a1116c36c2270e46a95f030200091f8de595c6c3426cd2`
  - AArch64: `f32da6712a897ce94594ee1473bb14cc9b8cdf7702483e860aef8a3b74c488f2`
- License: Apache-2.0
- License SHA-256:
  `1495e1e757ef4d0925a2350563cf5754bb23c51701a8ec4fb3c5cdcbedae6747`

`release-manifest.json` records exact hashes for the six qualified runtime
sources, their pristine upstream bases, and the six published overrides.

## Directions and qualified checkpoint

- Repository: `XiaomiMiMo/MiMo-V2.6-Pro-MOPD`
- Revision: `adea8e2c5373181e5a973fa1ecb343cb31af214b`
- Hidden width: 6,144
- Checkpoint tensor parallelism used for qualification: 8
- Serialized direction type: BF16 PyTorch tensors with typed provenance metadata
- Application: two manifest-order rank-one directions at alpha 2.0 on layers
  46-49, captured from layer 38 post-layer output

Both vectors were fitted on the same pinned Pro-MOPD checkpoint. The discovery
context used the checkpoint's baked system prompt. The portable manifest records
its effective SHA-256 without publishing the prompt text.

## Method provenance

The refusal-direction/abliteration workflow, boundary capture-and-freeze
methodology, and lambda-strength intervention framing were adapted from public
work by Keys (drowzeys). Blackfrost-AI performed the checkpoint-specific fit,
runtime implementation, pass selection, and release engineering. See
`CREDITS.md` for links and attribution boundaries.

## Publication exclusions

The release allowlist excludes virtual environments, full SGLang trees,
bytecode, compiled extensions, caches, logs, prompt text, prompt banks, captured
activations, evaluation results, model weights, tokenizer files, supervisor and
network configuration, credentials, and machine-specific paths.
