# Control Plane Repository (repo 47)

Repository 47 is the control-plane authority for a permanently coupled two-repository system:

- **repo 47**: orchestration, protocol, contracts, governance
- **repo 48**: runtime implementation (Solana program + TypeScript client)

This repository does **not** execute the runtime. It defines what the runtime must implement.

## Canonical topology

- repo 47 branches: `main`, `control`
- repo 48 branches: `main`, `runtime`

The two repositories remain separate, but they operate as one canonical system through shared manifests, contracts, and cross-repo validation.

## Key artifacts in repo 47

- `docs/system/TWO_REPO_SYSTEM.md` — architecture, branch strategy, sync rules, release flow
- `contracts/events/runtime_event.v1.schema.json` — example protocol event contract
- `contracts/shared/version-manifest.schema.json` — shared manifest schema used by both repos
- `manifests/system-manifest.json` — current compatibility manifest
- `.github/workflows/control-contract-gate.yml` — contract validation + repo 48 dispatch
- `.github/workflows/control-release-gate.yml` — stable release gate for `main`

## Rule of operation

`control` is source-of-truth for protocol contracts. `runtime` must conform before either `main` branch can advance.
