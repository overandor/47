# Coordinated Two-Repository System Governance

## Topology

- **Repository 47 (Control Plane)**
  - `main`: Latest stable compatible protocol release.
  - `control`: Active development of system specifications and contracts.
- **Repository 48 (Runtime Plane)**
  - `main`: Latest stable compatible implementation release.
  - `runtime`: Active development of Solana programs and execution logic.

## Synchronization Rules

1. **Source of Truth**: Repository 47 (`control` branch) is the canonical source for all protocol contracts and schemas.
2. **Conformity**: Repository 48 (`runtime` branch) must always conform to the contracts defined in Repo 47.
3. **Stability**: Both `main` branches must represent a synchronized, stable, and compatible state of the entire system.
4. **Validation**:
   - Changes in `47/control` trigger automated compatibility checks against `48/runtime`.
   - Changes in `48/runtime` must validate against `47/control` schemas.
5. **Release Flow**: Merges to `main` in both repos must be coordinated. No breaking change reaches `main` without cross-repo validation.

## Conflict Resolution

- In case of semantic mismatch, the Control Plane (Repo 47) takes precedence.
- Implementation constraints in Repo 48 that require protocol changes must be proposed via PRs to Repo 47 first.
