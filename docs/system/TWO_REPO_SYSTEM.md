# Two-Repository Coordinated System Design

## 1) Audit snapshot

### repo 47 (observed)
- Contains protocol-oriented documentation and prototype artifacts.
- Lacks explicit control-plane repository structure for cross-repo synchronization.

### repo 48 (reported input)
- Contains runtime seed implementation:
  - Rust Solana program skeleton
  - TypeScript client scaffold
  - client `package.json`

## 2) Target operating model

- **2 repositories, 4 branches, 1 canonical system**.
- Repositories remain physically separate.
- Compatibility is enforced by contracts + shared manifest + automated cross-repo checks.

## 3) Required branch topology

### repo 47 (control plane)
- `control`: authoritative contract/spec branch (source of truth).
- `main`: latest stable control-plane release compatible with repo 48 `main`.

### repo 48 (runtime plane)
- `runtime`: active implementation branch.
- `main`: latest stable runtime release compatible with repo 47 `main`.

## 4) Proposed repository structures

### repo 47 (control plane)

```text
repo-47/
  contracts/
    events/
      runtime_event.v1.schema.json
    messages/
      # future message schemas
    shared/
      version-manifest.schema.json
  manifests/
    system-manifest.json
  docs/
    system/
      TWO_REPO_SYSTEM.md
      GOVERNANCE.md              # future
      COMPATIBILITY_POLICY.md    # future
      RELEASE_PROCESS.md         # future
  roadmap/
    ROADMAP.md                   # future
  .github/workflows/
    control-contract-gate.yml
    control-release-gate.yml
```

### repo 48 (runtime plane)

```text
repo-48/
  programs/
    solana-core/                # Rust Solana program
  client/
    src/                        # TypeScript client
    package.json
  integration/
    contract-adapters/
    schema-loaders/
  deployment/
    scripts/
    env/
  tests/
    runtime/
    compatibility/
  manifests/
    system-manifest.json        # mirrored from repo 47 during sync
  .github/workflows/
    runtime-compat-gate.yml
    runtime-release-gate.yml
```

## 5) Synchronization workflow

1. Contract/spec change is authored in **repo 47 `control`**.
2. repo 47 CI validates schemas and manifest consistency.
3. repo 47 CI triggers repo 48 compatibility workflow (dispatch).
4. repo 48 `runtime` runs conformance tests against repo 47 `control` contracts.
5. If compatible, repo 48 updates/echoes shared manifest version and publishes validation result.
6. Promotion:
   - repo 47 `control` -> repo 47 `main`
   - repo 48 `runtime` -> repo 48 `main`
   only after cross-repo checks are green.

## 6) Compatibility rules (normative)

1. repo 47 `control` is source of truth for protocol contracts.
2. repo 48 `runtime` must conform to repo 47 `control` contracts.
3. Both `main` branches represent latest stable mutually-compatible release.
4. Changes in repo 47 `control` must trigger compatibility checks in repo 48 `runtime`.
5. Changes in repo 48 `runtime` must validate against repo 47 `control` schemas.
6. Breaking changes cannot merge to either `main` without cross-repo validation.
7. Every sync cycle must update shared version manifest.

## 7) Shared manifest policy

- Contract source branch + commit are pinned.
- Runtime source branch + commit are pinned.
- Compatibility state is explicit (`compatible`, `provisional`, `blocked`).
- Schema/event versions are listed and semver-governed.
- A sync cycle ID and timestamp provide traceability.

## 8) GitHub Actions plan

### In repo 47
- `control-contract-gate.yml`
  - triggers on push/PR to `control`
  - validates JSON schemas
  - validates `manifests/system-manifest.json` against manifest schema
  - dispatches validation request to repo 48 (`repository_dispatch`)

- `control-release-gate.yml`
  - triggers on PR into `main`
  - verifies manifest state is `compatible`
  - verifies cross-repo status check has passed
  - blocks merge otherwise

### In repo 48 (to implement there)
- `runtime-compat-gate.yml`
  - triggers on push/PR to `runtime` and repository_dispatch from repo 47
  - fetches repo 47 contract schemas at pinned ref
  - runs conformance checks and runtime integration tests
  - updates runtime-side manifest mirror

- `runtime-release-gate.yml`
  - triggers on PR into repo 48 `main`
  - requires conformance pass against repo 47 `main`

## 9) Release flow

### Contract-led release
1. Update contracts on repo 47 `control`.
2. Run cross-repo validation on repo 48 `runtime`.
3. If passed, update manifest compatibility and versions.
4. Merge repo 47 `control` -> `main`.
5. Merge repo 48 `runtime` -> `main`.
6. Tag both repos with same system version (`system-vX.Y.Z`).

### Runtime-led release (non-breaking)
1. Implement internal runtime changes on repo 48 `runtime`.
2. Validate against current repo 47 `control` contracts.
3. Update shared manifest runtime commit + sync metadata.
4. Promote to both `main` branches when compatibility remains `compatible`.

## 10) Breaking-change handling

- Breaking contract changes require:
  - schema major version bump,
  - migration notes,
  - coordinated PRs in both repos,
  - green cross-repo validation before any `main` merge.

## 11) Conflict resolution policy

1. Contract interpretation conflicts: repo 47 `control` schema is final.
2. Runtime feasibility conflicts: escalate with an RFC issue in repo 47.
3. Emergency mismatch on `main`: freeze both release pipelines and rollback to prior compatible manifest tuple.
4. Stale manifest state: fail closed (block release) until manifest is reconciled.

## 12) Governance controls

- Required status checks on all four protected branches.
- CODEOWNERS split:
  - protocol/governance owners in repo 47,
  - runtime owners in repo 48,
  - at least one approver from each side for breaking changes.
- Mandatory manifest update in each sync cycle.

## 13) Example control-runtime message instance

```json
{
  "event_id": "evt-8f1b8a2a",
  "event_type": "runtime.tx_confirmed",
  "spec_version": "v1",
  "system_version": "0.1.0",
  "origin": {
    "repo": "repo-48",
    "branch": "runtime",
    "component": "solana_program"
  },
  "payload": {
    "cluster": "devnet",
    "program_id": "6mWQk1...",
    "signature": "3Q5aT2...",
    "status": "confirmed",
    "error_code": null
  },
  "emitted_at_utc": "2026-04-16T12:05:00Z"
}
```

Schema authority: `contracts/events/runtime_event.v1.schema.json`.
