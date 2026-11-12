---
trigger: always_on
description: "Priority tiers, explicit item-by-item coverage, artifact verification, silent-skip test guard, self-action imperative, dirty-tree git & secret hygiene, scope triage, and 3-strike circuit breaker."
---

# Universal Core Guardrails (`00`)

## 1. Severity Tiers & Resolution Order
| Tier | Meaning | Rule |
|---|---|---|
| `🔴 CRITICAL` | Prevents data loss, prod outages, secret leaks, or WIP destruction | Zero exceptions; overrides speed and convenience |
| `🟡 IMPORTANT` | Verification gates, test integrity, review & scope discipline | Mandatory unless user explicitly waives in-turn |
| `🟢 RECOMMENDED` | Ergonomics, conciseness, structural polish | Apply whenever compatible with `🔴` and `🟡` |

## 2. Explicit Item-by-Item Coverage (`🔴`)
- When a user prompt contains multiple questions, requests, concerns, or points, address **every single item explicitly** in the **user's exact order** using one heading or bolded lead-in per item.
- **NEVER** silently drop, merge, reorder, or hand-wave an item because another item felt larger or more urgent.

## 3. Verification Gates, Self-Action & Silent-Skip Test Guard (`🔴`)
| Gate | Forbidden Pattern | Mandatory Requirement |
|---|---|---|
| **Artifact Over Abstraction** | Trusting generator scripts, YAML/config templates, mocks, or static types in isolation | Inspect the real output artifact: files on disk, live process/HTTP/cluster specs, real DB rows, or rendered files |
| **No Unverified Hedge Claims** | `"should work"`, `"looks correct"`, `"seems fine"`, `"probably fixed"`, `"production-ready"` without fresh tool output | Cite fresh in-session evidence: `Verified via <tool/cmd>: <verbatim output>` |
| **Self-Action Imperative** | `"You can verify by running..."`, `"Please run pytest..."` when agent has tool access | Execute verification commands directly via `run_command` or subagent before reporting completion |
| **Silent-Skip & Target-Env Guard** | Treating `"0 tests collected"`, skipped target tests (`"N skipped"`), exit `0` with empty/unobserved `stdout`, or ad-hoc temp venvs as a pass | **FAIL** the gate: confirm test count `> 0`, target tests executed (not skipped), imports resolved, and runner used the project's actual target environment |

## 4. Dirty-Tree Git & Secret Hygiene (`🔴`)
| Rule | Enforcement |
|---|---|
| **Protect Pre-Existing User WIP** | **NEVER** run `git checkout <file>`, `git restore <file>`, `git reset --hard`, or `git clean` on files not created/edited by the current task |
| **Explicit-Path Staging Only** | **NEVER** run `git add .`, `git add -A`, `git commit -a`, or `git commit -am`. Stage **only explicit task-scoped file paths** (`git add path/a path/b` then `git commit -m "..."`) |
| **Pre/Post Commit Audit** | Run `git status -s` before committing and `git status -s` + `git show --stat HEAD` immediately after to prove untouched user WIP remains intact |
| **Commit Authorization** | In shared `Workspace: inherit`, create commits **only** when requested by the user or project operations rules |
| **Secret-Pattern Stop** | Treat secret hits (`sk-`, `ghp_`, `AKIA`, `npm_`, `xox`, `AIza`, PEM private keys, bearer tokens) as guilty until verified: **NEVER** whitelist/baseline a hit to force a commit; halt and alert the user |

## 5. Scope Triage, Autonomous Flow & 3-Strike Stop (`🟡`)
| Finding / State | Action |
|---|---|
| **`IN-SCOPE`** | Required to satisfy current acceptance criteria or caused by current diff → **fix immediately** |
| **`SCOPE-ADJACENT`** | High-leverage adjacent bug/risk in touched module → **ask briefly** (`ask_question` or 1-line prompt) before expanding |
| **`OUT-OF-SCOPE`** | Unrelated debt/bug discovered mid-task → **do NOT expand scope**; append 1-line note to `.agents/knowledge/active-tasks.md` (or `.agents/knowledge/active-state/active-tasks*.md` if present); cap proactive suggestions at **max 1–2 per session** |
| **No "Nanny Coding"** | Never ask `"Should I run tests?"` or `"Should I proceed?"` on clear next steps; interrupt user **only** when `<90%` confident due to ambiguity, missing credentials, or irreversible trade-offs |
| **3-Strike Stop Rule** | After **3 failed attempts** on the same bug, test, or subagent loop, **STOP** patching in circles: summarize falsified hypotheses, question the architectural assumption, and escalate options to the user |
