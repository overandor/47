# repo 47 — Unchained Control Plane

repo 47 is the **control/data-dictionary repository** in a permanently coupled two-repository system.

- repo 47 branches: `control`, `main`
- repo 48 branches: `runtime`, `main`

repo 47 owns protocol authority; repo 48 executes minting/runtime behavior.

## What this repo now controls

- canonical entry schema: `control/unchained/schemas/entry.schema.json`
- canonical minted registry schema: `control/unchained/schemas/minted-registry.schema.json`
- control->runtime dispatch contract: `control/unchained/contracts/new-entry-batch.v1.json`
- data dictionaries: `data/dictionary/*.json`
- submitted entries: `data/entries/**`
- control-plane validation + dispatch workflow: `.github/workflows/control-entry-sync.yml`

## Runtime demo template (for repo 48)

A runnable runtime reference implementation is included at:

- `templates/repo48-runtime-demo/`

It contains TypeScript minting code, Pinata upload code, Solana NFT mint code, and a GitHub Actions workflow (`mint-on-upload.yml`) that supports push, schedule, workflow_dispatch, and repository_dispatch triggers.

## Security

Treat any previously pasted credentials as compromised. Revoke/rotate them and store replacements in GitHub Secrets only.
