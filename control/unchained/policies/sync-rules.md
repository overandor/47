# Unchained Sync Rules

1. New or changed `data/entries/**/*.json` in repo 47 `control` must validate against `entry.schema.json`.
2. repo 47 dispatches `new_entry_batch.v1` to repo 48 `runtime` after validation passes.
3. repo 48 runtime must mint and produce/update `registry/minted.json`.
4. repo 48 must validate minted records against `minted-registry.schema.json`.
5. repo 48 publishes back compatibility status and minted slugs.
6. repo 47 cannot promote to `main` unless latest dispatch cycle is acknowledged by repo 48.
