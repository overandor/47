# Two-Repository System (Unchained)

## Topology

- **repo 47** (control plane): branches `control`, `main`
- **repo 48** (runtime plane): branches `runtime`, `main`

Repos remain separate but are permanently coupled by schema contracts and CI dispatch.

## Responsibilities

### repo 47 (control)
- Owns schema contracts and dictionary constraints.
- Validates incoming entry files.
- Dispatches `new_entry_batch_v1` events to repo 48 runtime.
- Blocks stable promotion unless runtime compatibility is confirmed.

### repo 48 (runtime)
- Owns Solana/Pinata/LLM runtime logic.
- Mints NFTs from validated entry batches.
- Updates minted registry and reports status.

## Folder structure

### repo 47
```text
control/unchained/schemas/
control/unchained/contracts/
control/unchained/policies/
data/dictionary/
data/entries/
.github/workflows/control-entry-sync.yml
```

### repo 48 (target)
```text
programs/
client/
scripts/
src/
data/entries/
media/
registry/minted.json
.github/workflows/mint-on-upload.yml
```

## Sync workflow

1. Entry JSON is added to repo 47 `data/entries/**`.
2. `control-entry-sync.yml` validates entry + dictionary conformance.
3. repo 47 dispatches `new_entry_batch_v1` to repo 48.
4. repo 48 runtime mints NFT(s) and updates `registry/minted.json`.
5. repo 48 status feeds release gating for both `main` branches.

## Compatibility rules

1. repo 47 schemas are source-of-truth.
2. repo 48 runtime must parse and enforce repo 47 schema versions.
3. Breaking schema changes require version bump and coordinated rollout.
4. No merge to either `main` without cross-repo validation.
5. Every sync cycle updates shared manifest.

## Shared version manifest

Use `contracts/shared/version-manifest.schema.json` + `manifests/system-manifest.json`.

Required fields:
- system version
- sync cycle id/time
- compatibility state
- repo+branch+commit for control/runtime
- schema versions

## Release flow

### control-driven
- Update schema in repo 47 `control`.
- Dispatch and validate in repo 48 `runtime`.
- If compatible, promote to both `main` branches.

### runtime-driven (non-breaking)
- Update runtime internals in repo 48 `runtime`.
- Validate against current repo 47 schema.
- Promote to both `main` branches if compatible.

## Conflict policy

- Contract interpretation conflicts are resolved by repo 47 control schema.
- Runtime feasibility conflicts require coordinated RFC before release.
- Incompatibility on stable branches triggers rollback to last compatible manifest.
