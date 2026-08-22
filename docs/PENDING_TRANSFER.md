# Pending large/binary transfer

A pending-only transfer package has been prepared outside the repository for assets that cannot be moved reliably through the text-side GitHub connector.

Package name: `maize-class-source-domain-shift_GITHUB_PENDING_ONLY.zip`

Package SHA-256: `928dc861e744135f61dd4d84165e626bf27cabd55313dd4773646f81bfdc59eb`

The ZIP itself must **not** be committed. Its contents should be copied into the repository root while preserving paths.

Expected target-file hashes are versioned in `manifests/pending_transfer_expected_sha256.csv`. Run `python scripts/verify_pending_transfer.py` to verify any files already transferred, or `python scripts/verify_pending_transfer.py --require-all` after the whole package has been copied.

Current package contents include:

- release-safe full master-corpus manifest;
- release-safe full E2-A split manifest;
- two output-stripped/path-parameterized notebooks plus their audit;
- five current main analytical PDF figures;
- one explicitly named candidate supplementary training-time PDF.

The Grad-CAM image-bearing composite is intentionally excluded pending source-rights review. Per-image prediction outputs are not in this first pending package and remain a later transfer layer.
