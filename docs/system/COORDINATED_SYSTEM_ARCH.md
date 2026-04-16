# System Architecture: Coordinated Control and Runtime Planes

## Overview

The system is split into two specialized repositories to separate protocol definition from execution logic.

### Repo 47: Control Plane (The "Brain")
- **Responsibility**: Logic, contracts, and governance.
- **Source of Truth**: Dictates what the system *should* do.
- **Key Branches**: `main` (stable), `control` (active spec dev).

### Repo 48: Runtime Plane (The "Body")
- **Responsibility**: Implementation, execution, and integration.
- **Role**: Realizes the intent defined by the Control Plane.
- **Key Branches**: `main` (stable), `runtime` (active implementation dev).

## Synchronization Workflow

1. **Contract Definition**: A new message or event format is defined in Repo 47/control.
2. **Schema Validation**: Automated CI in Repo 47 validates the schema.
3. **Runtime Implementation**: Repo 48 pulls the new schema and implements the corresponding logic in the `runtime` branch.
4. **Compatibility Check**: Repo 48 CI validates the implementation against Repo 47/control.
5. **Coordinated Release**:
   - `47/control` is merged to `47/main`.
   - `48/runtime` is merged to `48/main`.
   - The version manifest is updated to reflect the new system-wide stable state.

## Compatibility Rules

- **Backward Compatibility**: New protocol versions should strive to support existing runtimes where possible.
- **Strict Compliance**: Runtimes MUST NOT diverge from the schemas defined in the Control Plane.
- **Versioning**: Semantic versioning is applied at the system level via the `version-manifest.json`.
