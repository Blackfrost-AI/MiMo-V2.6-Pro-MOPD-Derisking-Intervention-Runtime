# Compatibility

## Qualified

- Python 3.12
- SGLang 0.5.19
- NVIDIA RTX PRO 6000 Blackwell (SM120)
- Eight GPUs with tensor parallelism 8
- XiaomiMiMo MiMo-V2.6-Pro-MOPD revision
  `adea8e2c5373181e5a973fa1ecb343cb31af214b`
- FA4 attention and `flashinfer_mxfp4` MoE
- MiMo reasoning and tool-call parsers
- 262,144-token configured context

The MXFP4 compatibility code also originated from successful B300/SM103 work,
but this exact Pro pass-2 release was end-to-end exercised on SM120.

## Direction compatibility

The two direction tensors have width 6,144 and were fitted against the pinned
MiMo-V2.6-Pro-MOPD checkpoint. Discovery used that checkpoint's baked system
prompt with no request-level system message. The manifest records the effective
prompt hash, but prompt text and tokenizer/model files are intentionally absent.

These vectors cannot load on MiMo-V2.6-Flash checkpoints, whose hidden width is
4,096. The runtime raises `Blackfrost direction width mismatch` rather than
padding or projecting a vector.

## Not promised

- Other SGLang versions
- CPU, ROCm, or non-Blackwell CUDA execution
- DFlash or MTP speculative decoding
- Multinode tensor parallelism
- Different tokenizer or baked system-prompt behavior
- Stable behavior after changing alpha, target layers, checkpoint revision, or
  direction order

The loader is intentionally version-gated. Port the changes and repeat smoke,
quality, loop, tool-call, and workload evaluation instead of forcing the package
onto an unknown runtime.
