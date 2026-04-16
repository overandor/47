# Semantic Protocol Runtime Prototype

This is a single-file prototype of a terminal-native semantic protocol programming system.

## One-line core idea

A **terminal-native semantic protocol language** where the user writes **typed intent** instead of language-specific code, and the system automatically **lowers fragments into the best runtime or programming language** under explicit policy, capability, and verification constraints.

## Main file
- `semantic_protocol_runtime.py`

## Example protocol
```text
policy {
  optimize: latency > cost
  deterministic: true
  allow database[db.main]
  allow filesystem[*]
  allow network[slack.ops]
  deny shell[*]
  retries: 1
}

users := source @db.main "select id, email, score from users"
hot   := users -> filter score > 0.8 -> project [id, email, score] -> sort score -> limit 10
write! hot @file:"hot_users.jsonl"
notify! hot @slack.ops:"#risk"
```

## Quick start
```bash
python semantic_protocol_runtime.py init
python semantic_protocol_runtime.py explain examples/demo.spr
python semantic_protocol_runtime.py compile examples/demo.spr --out build
python semantic_protocol_runtime.py run examples/demo.spr --dry-run
python semantic_protocol_runtime.py run examples/demo.spr
```

## Semantic Model & Operators

The SPR language uses a canonical set of operators to express semantic intent:

- `:=` : Bind a value to a name.
- `->` : Apply a pure transform (e.g., `filter`, `project`, `map`, `sort`, `limit`).
- `!` : Trigger a side effect (e.g., `write!`, `notify!`).
- `@` : Bind to a specific runtime or resource (e.g., `@db.main`, `@file:"out.jsonl"`).
- `&` : Join two or more bindings.
- `|` : Fallback or alternative pipeline.
- `:` : Optional type annotation (e.g., `users : List[User]`).
- `~>` : Heuristic or approximate transform (LLM-assisted).
- `#` : Planner hint.

## Architecture

The system contains:
- **Semantic Parser**: Translates SPR source into a typed IR.
- **Graph Builder**: Constructs intent, effect, and dependency graphs for verification and planning.
- **Capability & Policy Checker**: Enforces security and optimization constraints declared in the `policy` block.
- **Planner & Cost Model**: Ranks and selects the best execution targets (SQL pushdown vs. local Python) based on policy and resource availability.
- **Lowering Engines**: Generates executable artifacts (SQL queries, Python scripts).
- **Execution Runtime**: Orchestrates the execution of the unified plan and manages local resources like the demo SQLite database.
