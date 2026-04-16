# Typed Protocol Language (TPL) — V1 Spec Draft

## 1) Purpose

TPL is a **semantic execution language** where users author a single protocol artifact that declares:

- data flow,
- effects,
- capabilities,
- constraints,
- optimization policy.

TPL source is **not tied to one implementation language**. A planner lowers fragments to target backends (SQL, Python, shell, HTTP, etc.) while preserving declared semantics.

## 2) Design principles

1. **Meaning first**: source expresses intent, not backend syntax.
2. **Effects are explicit**: side effects are visible and typed.
3. **Policy-bounded optimization**: planner can optimize only within declared constraints.
4. **Deterministic core**: canonical IR and verifier define legal behavior.
5. **Local overrides, global portability**: pin backend only where necessary.

## 3) Core entities

- **Value**: typed data object flowing through transforms.
- **Transform**: pure operation from input value(s) to output value(s).
- **Effect**: operation with side effects (`write!`, `notify!`, etc.).
- **Capability**: permission boundary for external resources.
- **Policy**: optimization and safety constraints.
- **Binding**: association between names and values/resources.

## 4) Canonical operators (V1)

- `:` type annotation or constraint
- `=` immutable value binding
- `:=` runtime/resource binding (late/materialized)
- `->` pure transform chain
- `!` side-effect invocation marker
- `@` runtime/resource placement
- `?` unresolved inferable parameter
- `|` fallback or alternation path
- `#` planner hint/annotation
- `~>` approximate/heuristic transform (policy-gated)

## 5) Minimal grammar sketch (informal)

```ebnf
program        := (policy_block | decl | effect_stmt | comment)*
policy_block   := "policy" "{" policy_item* "}"
policy_item    := identifier ":" value

decl           := identifier type_annot? ("=" |":=") expr placement?
type_annot     := ":" type_expr
placement      := "@" target

effect_stmt    := identifier "!" arg_list placement?

expr           := atom ("->" transform_call)* ("|" expr)?
transform_call := identifier arg_list?
arg_list       := (atom | kv_pair)+
```

Notes:
- Pure/data declarations use `=` by default.
- Resource-bound declarations use `:=`.
- Effects require `!`; implicit effects are invalid.

## 6) Type system (V1)

Mandatory categories:
- `Scalar<T>` (primitive wrappers)
- `Record{...}`
- `List<T>`
- `Stream<T>`
- `Table<T>`
- `Maybe<T>` / nullable

Type checks:
- transform input/output compatibility,
- effect argument compatibility,
- placement compatibility (`Stream<T>` sink to append-only target, etc.).

## 7) Effect model

Effect classes:
- `io.file`
- `io.network`
- `io.db`
- `notify`
- `exec.shell`

Rules:
- every effect must be explicitly marked with `!`;
- every effect must map to an allowed capability;
- effects are sequenced by dependency edges in the effect graph.

## 8) Policy model

`policy { ... }` may include:

- `optimize: latency > cost` (priority chain)
- `deterministic: true|false`
- `network: allow[...]|deny`
- `filesystem: allow[...]|deny`
- `shell: allow|deny`
- `retries: N`
- `max_cost: <budget>`

Planner must reject plans violating policy.

## 9) Capability model

Capabilities are explicit declarations (inline in V1 policy):

```tpl
policy {
  network: allow[api.main, slack.ops]
  filesystem: deny
  shell: deny
}
```

A lowering requiring denied capability is invalid even if functionally correct.

## 10) IR model

The compiler emits a canonical IR with:

- **Typed Intent Graph (TIG)**: nodes = transforms/effects; edges = data dependencies.
- **Effect Graph (EG)**: side-effect nodes and ordering constraints.
- **Constraint Set (CS)**: policy + type + capability constraints.
- **Candidate Lowerings (CL)**: backend realizations per node.

IR properties:
- stable serialization,
- deterministic hashing for replay,
- source span mapping for explainability.

## 11) Planning and lowering pipeline

1. Parse TPL source.
2. Build AST + symbol table.
3. Type-check and effect-check.
4. Build TIG + EG.
5. Generate candidate lowerings per node.
6. Score candidates by cost model and policy.
7. Solve for global plan (respecting dependencies/capabilities).
8. Emit backend code/actions.
9. Verify semantic conformance.
10. Execute with trace capture.

## 12) LLM role (bounded)

Allowed:
- propose candidate lowerings,
- fill unresolved `?` fields where type/policy permits,
- rank equivalent strategies.

Not allowed:
- change declared semantics,
- introduce undeclared effects,
- bypass policy/capability checks.

Any LLM output must be validated by deterministic verifier before execution.

## 13) Overrides / escape hatches

Local pinning examples:

```tpl
score := users -> map @python:local risk_model
agg := sales -> group region -> sum revenue @sql:pushdown
compress := blob -> transform @rust:ffi snappy
```

Pins apply only to the attached fragment, not global execution.

## 14) Example program (V1)

```tpl
policy {
  optimize: throughput > cost
  deterministic: false
  retries: 3
  network: allow[slack.ops]
  filesystem: allow[/tmp/reports]
}

users : Stream<User> := source @db "select id,email,status from users"
active = users -> where status="active"
scored = active -> map score_email -> filter score > 0.8 -> batch 100

write! scored @file:"/tmp/reports/highrisk.jsonl"
notify! count(scored) @slack:"#ops"
```

Possible realization:
- `source/where` lowered to SQL,
- `map score_email` lowered to Python,
- `batch/write` lowered to runtime + file IO,
- `notify!` lowered to Slack API call.

## 15) CLI / terminal UX (V1)

Proposed commands:

- `tpl check flow.tpl` — parse/type/effect/policy validation
- `tpl explain flow.tpl` — show TIG/EG and selected lowerings
- `tpl plan flow.tpl --opt latency` — materialize execution plan
- `tpl run flow.tpl` — execute plan
- `tpl pin flow.tpl node=3 target=python:local` — add local override
- `tpl replay <trace_id>` — deterministic replay (if deterministic mode)

## 16) Non-goals (V1)

- Full general-purpose language replacement.
- Unbounded natural-language programming.
- Autonomous semantic invention by model.
- Hidden side effects.

## 17) Acceptance criteria for MVP

A V1 prototype is successful if it demonstrates:

1. One-file protocol authoring for at least one real workflow.
2. Mixed lowering across at least two backends (e.g., SQL + Python).
3. Explicit side-effect tracking and policy enforcement.
4. `explain` output that maps source fragments to runtime actions.
5. Reproducible execution traces.

## 18) Open questions

- Optimal syntax for readable but strict effect declarations.
- Cost-model calibration across heterogeneous runtimes.
- Equivalence validation depth for approximate (`~>`) transforms.
- Packaging/distribution of reusable protocol libraries.

---

This draft defines a concrete path from the high-level concept to an implementable V1 language/runtime architecture.
