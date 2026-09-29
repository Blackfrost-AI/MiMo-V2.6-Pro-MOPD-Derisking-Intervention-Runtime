# Security notes

- The API launcher binds to `127.0.0.1` by default and does not add application
  authentication. Use a private network, authenticated proxy, or both.
- Direction paths are confined beneath the manifest directory, artifacts are
  verified against SHA-256 values, tensor payloads use `weights_only=True`, and
  vectors are checked for finite, nonzero, one-dimensional content.
- Only use manifests and artifacts from a trusted revision. A hash supplied by
  an untrusted manifest is not itself a trust boundary.
- `--trust-remote-code` executes code from the selected checkpoint repository.
  Pin and review its revision before deployment.
- This package contains no access tokens, SSH keys, service credentials, model
  weights, tokenizer files, prompt text, activations, evaluation traces, or
  compiled caches.
- Report package security issues privately to the repository owner rather than
  placing secrets or exploit details in a public discussion.
