# SGLang modifications

The following files are modified from SGLang 0.5.19 and redistributed under
Apache-2.0:

- `sglang/srt/configs/model_config.py`: recognize Xiaomi MXFP4 expert metadata.
- `sglang/srt/configs/qwen3_asr.py`: Transformers compatibility used by the
  qualified model-registry import path.
- `sglang/srt/layers/quantization/fp8.py`: propagate MXFP4 expert metadata and
  preserve the checkpoint scale representation.
- `sglang/srt/layers/quantization/mxfp4_flashinfer_trtllm_moe.py`: MXFP4 scale
  and loader compatibility.
- `sglang/srt/models/mimo_v2.py`: Xiaomi checkpoint-shard loading, MXFP4 scale
  handling, the reversible intervention hook, restricted tensor loading, path
  confinement, and finite/nonzero direction validation.
- `sglang/srt/models/mimo_vl.py`: Transformers compatibility used by the model
  registry import path.

The qualified files are stored under `overrides/`. The installer materializes a
private copy of the installed SGLang package and replaces only these six paths.
No installed package, checkpoint configuration, tokenizer, or weight file is
edited.
