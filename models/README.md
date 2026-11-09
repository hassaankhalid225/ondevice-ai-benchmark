# Models

Model binaries (`*.tflite`) are not committed. This folder holds the registry
(`manifest.yaml`) and instructions to reproduce the exact files.

## Steps
1. Download each model from its **official** source (record the URL in `manifest.yaml`).
   Prefer pre-converted LiteRT models from the official model zoo so both apps use a
   publicly reproducible artifact.
2. If you have to convert or quantise yourself, put the conversion script in
   `models/scripts/` and record the TensorFlow version. INT8 = full-integer post-training
   quantisation with a 100-image representative dataset (record which).
3. Compute hashes and fill `sha256` and `size_mb`:
   ```bash
   sha256sum models/*.tflite            # Windows PowerShell: Get-FileHash -Algorithm SHA256 <file>
   ```
4. Copy the files into both apps' asset folders (each app's README says where).
5. Commit `manifest.yaml` with message `feat(spec): pin model hashes`.

## Rules
- A model file never changes under the same `id` + `variant`. New file means a new id or variant, plus an ADR.
- Check each model's license allows redistribution before publishing the benchmark suite.
