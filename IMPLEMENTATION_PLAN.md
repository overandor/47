# TPL V1 Implementation Plan (4-Week Prototype)

This document continues `SPEC.md` with execution-level detail: concrete artifacts, module boundaries, deterministic behavior, and a build plan for a working prototype.

## 1) Scope for the first runnable prototype

### In-scope
- Parser for a strict TPL subset.
- Typed Intent Graph (TIG) and Effect Graph (EG).
- Capabilities + policy validation.
- Mixed lowering to:
  - SQL (SQLite/Postgres-compatible subset),
  - Python runtime,
  - HTTP calls.
- CLI commands:
  - `check`,
  - `explain`,
  - `plan`,
  - `run`.
- Deterministic trace capture and replay seed.

### Out-of-scope (prototype)
- GPU lowering.
- Distributed scheduling.
- Probabilistic transforms (`~>`) beyond syntax acceptance.
- Full optimizer search.

## 2) Concrete architecture

```text
TPL source
  -> lexer/parser
  -> AST
  -> type/effect checker
  -> canonical IR (TIG + EG + constraints)
  -> planner (candidate generation + scoring)
  -> lowerers (sql, python, http)
  -> verifier (policy + shape + effect checks)
  -> executor
  -> trace store
```

## 3) Module boundaries

- `parser/`
  - Tokenizer + grammar parser.
- `semantics/`
  - Type inference/checking.
  - Effect classification.
- `ir/`
  - Canonical node/edge schema.
  - Stable serialization.
- `planner/`
  - Candidate lowerings.
  - Cost scoring.
  - Plan selection.
- `lowerers/`
  - `sql.py`, `python.py`, `http.py`.
- `verifier/`
  - Capability/policy enforcement.
  - I/O shape checks.
- `runtime/`
  - Execution engine.
  - Retry/idempotency controls.
- `cli/`
  - Command entrypoints.

## 4) Canonical IR schema (prototype)

```json
{
  "program_id": "sha256(source+version)",
  "nodes": [
    {
      "id": "n1",
      "kind": "source|transform|effect",
      "op": "source|where|map|filter|write|notify",
      "input_types": ["Stream<User>"],
      "output_type": "Stream<User>",
      "effects": [],
      "constraints": {"deterministic": true},
      "source_span": {"line": 12, "col": 1}
    }
  ],
  "edges": [
    {"from": "n1", "to": "n2", "kind": "data"},
    {"from": "n4", "to": "n5", "kind": "effect_order"}
  ],
  "policy": {
    "optimize": ["latency", "cost"],
    "deterministic": true,
    "capabilities": {
      "network": ["api.main", "slack.ops"],
      "filesystem": [],
      "shell": false
    }
  }
}
```

Determinism rules:
- Node IDs are hash-derived from canonicalized subtrees.
- Policy object is normalized before hashing.
- Plan hash includes selected lowerings + runtime versions.

## 5) Planner algorithm (deterministic baseline)

1. Enumerate legal lowerings per node.
2. Remove candidates violating capabilities/policy.
3. Score each candidate with fixed weighted metrics.
4. Choose best candidate per node.
5. Resolve cross-node incompatibilities with tie-break rules.
6. Emit final plan + reason codes.

### Baseline cost function

`score = w_latency * est_latency + w_cost * est_cost + w_risk * est_risk`

Tie-break order:
1. deterministic backend,
2. fewer network effects,
3. lower generated LOC,
4. lexical backend order (`python < sql < http`).

## 6) LLM integration contract

LLM is optional and can only operate in two steps:

1. **Candidate Proposal**: suggest additional lowerings with structured output.
2. **Ranking Hint**: provide preference among legal candidates.

Hard boundaries:
- LLM cannot output executable code directly into runtime path.
- All LLM outputs must be translated into candidate metadata then revalidated.
- If LLM is unavailable, planner must still produce a plan.

## 7) Verifier checks before execution

- Type compatibility across all data edges.
- No undeclared effects.
- All effects map to allowed capabilities.
- All placements resolve to available adapters.
- Determinism mode blocks nondeterministic operations.
- Retry policy valid for each effect type.

If any check fails: no partial execution.

## 8) CLI behavior (prototype)

### `tpl check file.tpl`
- Parse + semantic checks only.
- Exit code `0` on valid, `2` on validation errors.

### `tpl explain file.tpl`
- Print:
  - TIG nodes/edges,
  - EG sequence,
  - candidate lowerings,
  - rejected candidates with reason.

### `tpl plan file.tpl --json`
- Output materialized plan with plan hash.

### `tpl run file.tpl`
- Execute finalized plan.
- Emit trace ID and effect summary.

## 9) Trace and replay format

Each run stores:
- `trace_id`
- `program_hash`
- `plan_hash`
- timestamp
- node execution records
- effect records (target, payload hash, status)
- policy snapshot

Replay semantics:
- In deterministic mode, plan hash must match.
- If adapters changed, replay is blocked unless `--allow-adapter-drift`.

## 10) Security defaults

- Deny shell execution by default.
- Deny filesystem writes by default.
- Allowlisted network endpoints only.
- Secrets referenced by name, never inline in source.
- Effect payloads redacted in logs by policy.
- Runtime adapters load credentials from environment variables (for example, `JULES_API_KEY`) and fail fast if missing.

## 11) Test strategy

### Unit tests
- Parser snapshots.
- Type/effect checker cases.
- Policy/capability rejection cases.
- Lowerer correctness for each backend adapter.

### Integration tests
- One SQL+Python mixed lowering flow.
- One HTTP side-effect flow with retries.
- One denied-capability failure flow.

### Golden tests
- `explain` and `plan --json` outputs are stable.

## 12) 4-week execution plan

### Week 1
- Parser + AST + minimal type checker.
- Basic CLI skeleton (`check`).

### Week 2
- IR builder + policy/capability verifier.
- `explain` command.

### Week 3
- SQL/Python/HTTP lowerers.
- Planner scoring + deterministic tie-breakers.
- `plan` command.

### Week 4
- Runtime executor + traces.
- `run` command.
- Integration tests and demo script.

## 13) Demo acceptance script

Target demo:
1. Load users from SQL.
2. Score in Python transform.
3. Notify over HTTP webhook.
4. Show `explain` output with mixed lowerings.
5. Show trace and replay check.

Success metric:
- Single TPL file executes end-to-end with policy enforcement and auditable plan.
