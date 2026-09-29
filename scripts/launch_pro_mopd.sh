#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
PYTHON_BIN=${PYTHON_BIN:-python3}
OVERLAY_DIR=${OVERLAY_DIR:-${ROOT}/runtime-overlay}
INTERVENTION_MANIFEST=${INTERVENTION_MANIFEST:-${ROOT}/artifacts/pro-mopd-prompt32-pass2-lambda2/manifest.json}
: "${MODEL_PATH:?Set MODEL_PATH to the pinned local MiMo-V2.6-Pro-MOPD checkpoint directory}"

if [[ ! -f "${OVERLAY_DIR}/blackfrost-overlay.json" ]]; then
  "${PYTHON_BIN}" "${ROOT}/scripts/materialize_overlay.py" --output "${OVERLAY_DIR}"
fi
"${PYTHON_BIN}" "${ROOT}/scripts/verify_package.py"

export BLACKFROST_MIMO_MOE_INTERVENTION="${INTERVENTION_MANIFEST}"
export CUDA_DEVICE_ORDER=${CUDA_DEVICE_ORDER:-PCI_BUS_ID}
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}
export PYTHONPATH="${OVERLAY_DIR}${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONNOUSERSITE=${PYTHONNOUSERSITE:-1}
export TOKENIZERS_PARALLELISM=${TOKENIZERS_PARALLELISM:-false}
export PYTHONUNBUFFERED=${PYTHONUNBUFFERED:-1}
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
export SGLANG_CACHE_DIR=${SGLANG_CACHE_DIR:-${ROOT}/cache/sglang}
export TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-${ROOT}/cache/torchinductor}
export TRITON_CACHE_DIR=${TRITON_CACHE_DIR:-${ROOT}/cache/triton}
export FLASHINFER_WORKSPACE_BASE=${FLASHINFER_WORKSPACE_BASE:-${SGLANG_CACHE_DIR}}
export NCCL_DEBUG=${NCCL_DEBUG:-WARN}

mkdir -p "${SGLANG_CACHE_DIR}" "${TORCHINDUCTOR_CACHE_DIR}" "${TRITON_CACHE_DIR}"

exec "${PYTHON_BIN}" -m sglang.launch_server \
  --model-path "${MODEL_PATH}" \
  --served-model-name "${SERVED_MODEL_NAME:-mimo-2.6-pro}" \
  --trust-remote-code \
  --tp-size "${TP_SIZE:-8}" \
  --attention-backend "${ATTENTION_BACKEND:-fa4}" \
  --mm-attention-backend "${MM_ATTENTION_BACKEND:-fa4}" \
  --moe-runner-backend "${MOE_RUNNER_BACKEND:-flashinfer_mxfp4}" \
  --disable-flashinfer-autotune \
  --disable-custom-all-reduce \
  --mem-fraction-static "${MEM_FRACTION_STATIC:-0.90}" \
  --context-length "${CONTEXT_LENGTH:-262144}" \
  --max-running-requests "${MAX_RUNNING_REQUESTS:-8}" \
  --chunked-prefill-size "${CHUNKED_PREFILL_SIZE:-4096}" \
  --max-prefill-tokens "${MAX_PREFILL_TOKENS:-16384}" \
  --swa-full-tokens-ratio "${SWA_FULL_TOKENS_RATIO:-0.08}" \
  --page-size "${PAGE_SIZE:-1}" \
  --model-loader-extra-config "${MODEL_LOADER_EXTRA_CONFIG:-{\"enable_multithread_load\":true,\"num_threads\":64}}" \
  --reasoning-parser mimo \
  --tool-call-parser mimo \
  --cuda-graph-max-bs-decode "${CUDA_GRAPH_MAX_BS_DECODE:-8}" \
  --cuda-graph-bs-decode 1 2 4 8 \
  --cuda-graph-backend-prefill disabled \
  --skip-server-warmup \
  --enable-metrics \
  --host "${HOST:-127.0.0.1}" \
  --port "${PORT:-30000}" \
  "$@"
