# CLAUDE.md — syn

This repository defines **syn**, a command-line based synesthetic engine.
Claude Code is expected to follow the rules and intentions described here.

---

## Project Philosophy

syn is not a generic utility.
It is a **mode-based system** where the user's attitude is fixed at startup.

- syn converts sound into color via interpretation.
- Interpretation is mediated by an LLM.
- The system intentionally supports **two incompatible modes**:
  - research (reproducible)
  - live (ephemeral)

These modes must NEVER be mixed during a session.

---

## Core Principles (Non-Negotiable)

1. **Mode is selected ONLY at startup**
   - `syn start research`
   - `syn start live`
   - No runtime mode switching is allowed.

2. **CLI is a declaration, not a toggle**
   - Starting syn is equivalent to declaring intent.
   - Avoid interactive prompts that change core behavior.

3. **Prompts define behavior**
   - LLM behavior is governed exclusively by files in `/prompts`.
   - Do not inline or duplicate prompt logic elsewhere.

4. **Reproducibility vs Ephemerality is enforced structurally**
   - research logs are reproducible
   - live logs are non-reproducible traces
   - Design choices must respect this separation.

---

## Project Structure Expectations

Claude Code should respect and extend the following structure:

```Plain text
synesthesia/
├─ syn/
│ ├─ cli.py
│ ├─ session.py
│ ├─ modes/
│ │ ├─ research.py
│ │ └─ live.py
│ ├─ llm/
│ └─ core/
├─ prompts/
│ ├─ research.md
│ └─ live.md
└─ logs/
├─ research/
└─ live/
```

- `/prompts` is authoritative.
- `/modes` should contain minimal logic, delegating interpretation to LLM.
- `/cli.py` should only parse arguments and start a session.

---

## CLI Specification (Strict)

Supported commands:

```bash
syn start research [options]
syn start live [options]
```

Rules:

- start is the only top-level verb.
- research and live are the only valid modes.
- Invalid modes must result in an immediate error.
- No aliases, no shorthand flags for modes.

### Research Mode Options

Allowed:

- `--seed`
- `--key`
- `--log`

Disallowed:

- randomness flags
- live-style options

### Live Mode Options

Allowed:

- `--key`
- `--session`

Disallowed:

- `--seed`
- any reproducibility-related flags

Claude Code must not add extra options unless explicitly instructed.

## Logging Rules

- research mode:
  - logs must be structured
  - outputs must be reproducible
  - suitable for comparison
- live mode:
  - logs are traces, not guarantees
  - no attempt to restore sessions
  - logs may omit parameters intentionally

## LLM Usage Rules

- LLM calls MUST:
  - load prompt text from /prompts
  - return structured numeric JSON
  - avoid explanations, prose, or comments
- Claude Code must NOT:
  - embed prompt text in code
  - modify prompts without explicit instruction
  - mix research and live prompt logic

## What Claude Code Should Optimize For

- Clarity over cleverness
- Structural enforcement of philosophy
- Minimal surface area
- Explicit failure on invalid states

Avoid:

- Feature creep
- Implicit defaults that change behavior
- Interactive UI patterns

## When in Doubt

If there is ambiguity:

1. Prefer less functionality
2. Prefer explicit failure
3. Preserve the philosophical separation of modes

If a design choice threatens the integrity of `research` vs `live`,
it is the wrong choice.
