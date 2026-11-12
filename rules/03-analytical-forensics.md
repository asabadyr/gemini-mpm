---
trigger: model_decision
description: "Activate when producing metrics, cost or utilization reports, log forensics, DB count/rate queries, performance benchmarks, or root-cause data analysis."
---

# Analytical & Data Forensics Protocol (`03`)

## Mandatory 6-Point Visible Self-Check (`🔴`)
Whenever producing a metric summary, cost/utilization report, DB count/rate query, benchmark comparison, or diagnostic conclusion from logs/telemetry, append an explicit **`Visible Self-Check`** block verifying all 6 invariants before presenting conclusions:

| # | Check | Trap Prevented | Verification Required |
|---|---|---|---|
| **1** | **Dimensional & Unit Consistency** | Mixing `s` vs `ms` vs `ns` timestamps; `B` vs `KB` (`10^3`) vs `MiB`/`GiB` (`2^20`/`2^30`); raw payload vs wire size after base64 (`× 4/3` + framing/CRLF) | Write unit conversions explicitly; verify `rate × window == total` |
| **2** | **Time-Series Aggregation Semantics** | Summing gauge window averages (`avg_over_time` / bucket means) across windows where short-lived batch jobs or bursts inflate cost or load by `10×+` | Weight gauges by actual runtime duration, or integrate true monotonic counters/rates (`rate()` / `increase()`) |
| **3** | **Denominator & Population Survival** | Computing failure/adoption rates over raw table counts containing soft-deleted (`deleted: true`), disabled, offboarded, or unmonitored entities | State exact `Numerator / Denominator` filters and reconcile across joined entity/credential tables |
| **4** | **Control Cohort Baseline** | Attributing a metric drop/spike in Cohort A to a local deploy when an upstream provider or global traffic shift caused it | Compare Cohort A against unchanged Control Cohorts over the identical time window |
| **5** | **Artifact Over Abstraction** | Inferring production state from IaC templates, Helm/YAML defaults, or report-generator code | Query live runtime specs, real DB rows, raw log lines, or rendered output files |
| **6** | **Single-Hypothesis Falsification** | Confirmation bias—cherry-picking logs that fit a first guess while ignoring contradicting timestamps or error codes | State one measurable hypothesis at a time, check for disconfirming evidence first, and separate observed facts from inference |

## Required Output Footer Template
Include a concise `### Visible Self-Check` section at the end of analytical deliverables covering items `1–6` (mark `N/A — <reason>` only for items genuinely absent, such as Cohort Controls on single-node local benchmarks).
