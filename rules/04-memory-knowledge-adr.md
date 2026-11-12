---
trigger: model_decision
description: "Activate when user states persistent rules ('remember', 'always', 'never', 'going forward'), after postmortems, when writing architecture docs or ADRs, or updating .agents/knowledge/."
---

# Memory, Knowledge Authority & ADR Discipline (`04`)

## 1. Implicit Memory Triggers & `/learn` Bridge (`🟡`)
- **Auto-Capture Triggers**: When the user states a persistent preference/constraint (`"remember"`, `"from now on"`, `"going forward"`, `"always"`, `"never"`), corrects an agent mistake, or resolves a non-obvious operational trap:
  1. Immediately record a 1-line dated fact in `.agents/knowledge/memories.md` (if `.agents/knowledge/` exists in the workspace).
  2. When the lesson should persist as a reusable cross-session rule or workflow skill, recommend Antigravity's native `/learn` slash command.

## 2. Typed 5-Section `memories.md` Schema (`FIFO` Bounded `<=4 KB`)
Format every entry as a single line: `- [YYYY-MM-DD] <concise, actionable fact>` (no multi-paragraph prose).

| Section | Max Entries | Eviction Policy When Full | What Belongs Here |
|---|---|---|---|
| `## CRITICAL` | `20` | **NEVER auto-evict** (alert user at 20; move—never duplicate—when promoting from below) | Red-line safety invariants, destructive-op traps, hard constraints |
| `## Environment` | `15` | **FIFO (oldest-first)**: delete top-most oldest entry, append newest at bottom | Runtime quirks, non-git umbrella topology, toolchain/cluster paths |
| `## Decisions` | `20` | **FIFO (oldest-first)** | Architectural choices recording *why* option X beat Y |
| `## Patterns` | `20` | **FIFO (oldest-first)** | Canonical repo idioms, naming/testing conventions |
| `## Gotchas` | `15` | **FIFO (oldest-first)** | Non-obvious API/DB/deploy traps & past bug root causes |

- **Size Cap**: Keep `memories.md` **`<=4 KB` (`4,096` bytes)**. Multi-paragraph incident timelines belong in `.agents/knowledge/postmortems.md` (or `.agents/knowledge/active-state/*postmortems*.md`), cross-referenced in `00-INDEX.md`.

## 3. Chronological Authority Matrix (`00-INDEX.md`)
- Maintain `> **Last Consolidated / Verified:** YYYY-MM-DD` headers on `.agents/knowledge/` documents.
- **Conflict Resolution**: When older architecture prose conflicts with newer dated postmortems, `00-INDEX.md` authority rows, or live code/commits, **the newer verified timestamp + live code win**. Update stale entries rather than leaving contradictory notes.

## 4. 3-Gate Nygard ADRs & `WHAT`/`WHY` Docstrings
- **3-Gate ADR Filter (`docs/adr/NNNN-kebab-title.md`)**: Create an ADR (`Status: Proposed | Accepted | Superseded by NNNN`, Context, Decision, Consequences) **only** when **all 3 gates** hold:
  1. Architecturally significant (cross-module, data model, protocol, or security boundary),
  2. Costly to reverse once deployed,
  3. Rationale & rejected alternatives are non-obvious from reading code alone.
- **`WHAT` / `WHY` Docstrings (Never `HOW`)**: Public module/function docstrings state **WHAT** (observable contract, units, error conditions) and **WHY** (business/operational constraint), leaving **HOW** to clean code and inline comments on tricky invariants.
- **Spec-Link Precision Warning**: Zero-shot LLM `SPEC-*` trace links average `~0.52` precision—verify every linked requirement ID semantically before committing.
