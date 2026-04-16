# Coordinated Control Plane (Repo 47)

This repository serves as the **Control Plane** for the coordinated two-repository system. It is the authoritative source for protocol specifications, contracts, governance, and system-wide orchestration.

## Topology

- **Repo 47 (Control Plane)**: Governance, Contracts, Specs.
- **Repo 48 (Runtime Plane)**: Implementation, Execution, Integration.

## Key Branches

- `main`: Latest stable compatible protocol release.
- `control`: Active development of system specifications and contracts.

## Folder Structure

- `contracts/schemas/`: Canonical JSON schemas for events and manifests.
- `specs/`: Detailed protocol and architectural specifications.
- `governance/`: Synchronization rules and conflict resolution policies.
- `manifests/`: System-wide version manifests.
- `scripts/`: Validation and coordination scripts.

## Synchronization

This repository coordinates with **Repository 48 (Runtime Plane)**. Changes to the `control` branch trigger compatibility checks in the Runtime Plane. No breaking changes reach `main` without cross-repo validation.

For details on the coordinated architecture, see [docs/system/COORDINATED_SYSTEM_ARCH.md](docs/system/COORDINATED_SYSTEM_ARCH.md).
