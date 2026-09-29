---
license: apache-2.0
library_name: sglang
pipeline_tag: text-generation
base_model:
  - XiaomiMiMo/MiMo-V2.6-Pro-MOPD
tags:
  - sglang
  - mimo
  - mimo-v2.6
  - mixture-of-experts
  - mxfp4
  - blackwell
  - runtime-intervention
  - representation-engineering
  - security-research
inference: false
---

# MiMo V2.6 Pro MOPD SGLang Intervention Runtime

Canonical runtime artifacts are published on
[Hugging Face](https://huggingface.co/Blackfrost-AI/MiMo-V2.6-Pro-MOPD-Derisking-Intervention-Runtime).

This repository packages the Blackfrost-AI SGLang compatibility layer and the
reversible pass-2 runtime intervention used to serve MiMo V2.6 Pro MOPD on
NVIDIA Blackwell. It is a runtime package, not a model checkpoint. Model
weights, tokenizer files, prompt text, captured activations, evaluation traces,
compiled kernels, and deployment credentials are not included.

The included release contains:

- six qualified SGLang 0.5.19 overrides for the MiMo MXFP4 path;
- an isolated-overlay installer that never edits the shared Python environment;
- two 6,144-dimensional BF16 direction artifacts and a portable manifest;
- a TP8 launch profile matching the qualified 8-GPU deployment;
- exact source revisions, hashes, compatibility limits, and third-party notices.

## Method credit

The refusal-direction/abliteration workflow, boundary capture-and-freeze
methodology, and lambda-strength intervention framing are derived from public
work by **Keys (drowzeys)**. Blackfrost-AI adapted and refit the method for
MiMo-V2.6-Pro-MOPD, implemented the SGLang runtime loader, and ran the iterative
pass evaluation. Keys/drowzeys did not author these exact direction tensors and
is not implied to endorse this release. See [`CREDITS.md`](CREDITS.md).

## Tested configuration

| Component | Tested value |
|---|---|
| Checkpoint | `XiaomiMiMo/MiMo-V2.6-Pro-MOPD` |
| Checkpoint revision | `adea8e2c5373181e5a973fa1ecb343cb31af214b` |
| Direction fit | Same pinned Pro-MOPD checkpoint, two iterative passes |
| Runtime | SGLang 0.5.19 |
| GPU topology | 8 x RTX PRO 6000 Blackwell, TP8 |
| Attention / MoE | FA4 / FlashInfer MXFP4 |
| Context | 262,144 tokens |
| Thinking / tools | MiMo reasoning and tool-call parsers |

Pass 2 was selected from five experimental passes using automated marker-based
triage plus separate control prompts. That triage is not semantic review, a
broad quality benchmark, or a safety guarantee. Revalidate the intervention on
your own workload before deployment.

## Install

Use an environment that already has the GPU-specific SGLang stack installed.
The exact versions observed in the qualified environment are recorded in
[`environment-tested.txt`](environment-tested.txt). CUDA, PyTorch, FlashInfer,
and FlashAttention wheels are platform-specific, so this repository does not
replace them.

```bash
hf download Blackfrost-AI/MiMo-V2.6-Pro-MOPD-Derisking-Intervention-Runtime \
  --local-dir mimo-pro-runtime

python3 mimo-pro-runtime/scripts/verify_package.py
python3 mimo-pro-runtime/scripts/materialize_overlay.py \
  --output mimo-pro-runtime/runtime-overlay
```

`materialize_overlay.py` requires a pristine `sglang==0.5.19`. It verifies the
six upstream base hashes, copies the installed package into a private overlay,
applies the qualified overrides, and records the base environment. An extracted
official package can instead be supplied with `--base-package`.

Download the pinned checkpoint separately:

```bash
hf download XiaomiMiMo/MiMo-V2.6-Pro-MOPD \
  --revision adea8e2c5373181e5a973fa1ecb343cb31af214b \
  --local-dir /models/MiMo-V2.6-Pro-MOPD
```

## Serve

The defaults reproduce the qualified TP8 profile:

```bash
MODEL_PATH=/models/MiMo-V2.6-Pro-MOPD \
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
HOST=127.0.0.1 \
PORT=30000 \
  bash mimo-pro-runtime/scripts/launch_pro_mopd.sh
```

The launcher defaults to the cumulative two-direction pass-2 manifest with
alpha 2.0 per direction, source layer 38, and target layers 46-49. The API model
ID defaults to `mimo-2.6-pro`. Override
`INTERVENTION_MANIFEST` to use another compatible manifest. To measure a
loader-only baseline, launch SGLang directly through the materialized overlay
without setting `BLACKFROST_MIMO_MOE_INTERVENTION`.

Additional SGLang arguments can be appended to the launcher. It binds to
loopback by default; place authentication or a private network in front of it
before allowing remote clients.

## Verify the live API

```bash
python3 mimo-pro-runtime/scripts/smoke_test.py \
  --base-url http://127.0.0.1:30000/v1
```

The smoke test checks `/models` and submits a deterministic chat completion.

## What the intervention does

At each configured layer, the runtime applies both rank-one projections after
the down-projected MLP/MoE output:

```text
y <- y - alpha * d * (d^T y)
```

Vectors are normalized and re-orthogonalized in manifest order at load time.
The implementation checks the schema, provenance metadata, SHA-256 hashes,
orientation, target layers, alpha values, hidden width, finite values, and path
confinement before placing vectors on GPU. Tensor payloads use PyTorch's
restricted `weights_only` loader. Router decisions and model weights are not
modified.

Set `BLACKFROST_MIMO_MOE_INTERVENTION` before importing or launching SGLang;
configuration is cached per process.

## Scope

- Model weights remain governed by their upstream repository terms.
- The runtime overrides are modifications of Apache-2.0 SGLang 0.5.19.
- Blackfrost-AI releases its runtime changes and included direction artifacts
  under Apache-2.0.
- The package is research software and should be requalified after changing the
  checkpoint, tokenizer/system prompt, runtime, GPU architecture, alpha, or
  direction set.

See [`COMPATIBILITY.md`](COMPATIBILITY.md),
[`MODIFICATIONS.md`](MODIFICATIONS.md), [`PROVENANCE.md`](PROVENANCE.md),
[`SECURITY.md`](SECURITY.md), and
[`release-manifest.json`](release-manifest.json) before adapting the runtime.
