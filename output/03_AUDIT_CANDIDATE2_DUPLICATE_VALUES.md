# Audit: Candidate 2 — Duplicate Values in `pii.geographies` and `intent.supported`

## Status: ✅ CONFIRMED — Reproducible Validation Gap

## Claim

The `check()` function in `guardrails_runner.py` validates individual values in `pii.geographies` and `intent.supported` but does not check for duplicates. Configs with duplicate entries pass validation silently.

## Reproduction

```bash
python -c "
import sys; sys.path.insert(0, 'skills/unvibecode_gaurdrails_implemenataion_pack/Pre-configured_gaurdrails_programs')
from guardrails_runner import *
c = make_profile('chatbot')
c['pii']['geographies'] = ['IN', 'IN', 'US']
r = check(c)
print('Duplicate geo - Valid:', r['configuration_valid'])
c2 = make_profile('chatbot')
c2['intent']['supported'] = ['invoice', 'invoice', 'refund']
r2 = check(c2)
print('Duplicate intent - Valid:', r2['configuration_valid'])
"
```

**Output (confirmed on Python 3.12, Windows):**
```
Duplicate geo - Valid: True
Duplicate intent - Valid: True
```

## Root Cause

### Geography validation (line 183-184)
```python
if (not isinstance(pii["geographies"], list) or not pii["geographies"]
        or any(not isinstance(g, str) or g not in ("IN", "US", "GB", "SG", "AU", "CA") for g in pii["geographies"])):
```
Checks: is it a list? Is it non-empty? Are all values valid geography codes?
**Missing:** Are all values unique?

### Intent validation (line 191-192)
```python
if not isinstance(supported, list) or not supported or any(not isinstance(v, str) or not v for v in supported):
```
Checks: is it a list? Is it non-empty? Are all values non-empty strings?
**Missing:** Are all values unique?

## Internal Consistency Analysis

The author demonstrably cares about duplicates elsewhere in the same file:

| Layer | Duplicate Handling | Location |
|---|---|---|
| JSON keys | ✅ **Rejected** — `raise ValueError("Duplicate JSON key.")` | `read_config()`, L98-99 |
| README docs | ✅ Explicitly documented: "duplicate JSON keys are rejected" | README L27 |
| Control names | ✅ **Rejected** — `set(value) != set(expected)` | `shape()`, L122 |
| Geography list values | ❌ **Not checked** | `check()`, L183-184 |
| Intent label list values | ❌ **Not checked** | `check()`, L191-192 |

This inconsistency makes the gap a defect, not a deliberate design choice.

## Counter-Arguments Addressed

| Counter-Argument | Rebuttal |
|---|---|
| "Duplicates are harmless — Presidio handles them idempotently" | The checker's purpose is to catch config errors *before* deployment. A duplicate geography is a config error regardless of runtime behavior. |
| "The checker intentionally allows duplicates for flexibility" | No documentation states this. The JSON-key duplicate check proves the author cares about duplicates. |
| "Too minor to matter" | For `intent.supported`, duplicate labels could bias a trained classifier. The checker already validates labels (non-empty, strings-only) — just not uniqueness. |

## Suggested Fix

```python
# After line 184 (geography validation):
if len(pii["geographies"]) != len(set(pii["geographies"])):
    error("DUPLICATE_GEOGRAPHY", "pii.geographies", "Remove duplicate geography codes.")

# After line 192 (intent validation):
if len(supported) != len(set(supported)):
    error("DUPLICATE_INTENT", "intent.supported", "Remove duplicate intent labels.")
```

## Engineering Principles Alignment

| Principle | Violation |
|---|---|
| **Separation of Concerns** | The checker's documented job is config validation. Allowing duplicates delegates error detection to runtime. |
| **DDD / Clean Architecture** | `geographies` is semantically a set (a union of jurisdictions). `["IN", "IN", "US"]` is not a clean domain declaration. |
| **Anti-Pattern LLM-4 (Vibe-Based Evaluation)** | The checker validates many properties but this edge case was missed — suggesting incomplete test coverage. |

## Cohort 3 Scoring Assessment

| Criterion | Points | Assessment |
|---|---:|---|
| Technical depth | 35 | 18-23/35 — straightforward root cause, but internal-consistency argument adds depth |
| Reproducibility | 30 | 22-27/30 — deterministic 3-line repro, code locations pinpointed |
| Real developer impact | 20 | 10-14/20 — low practical impact; validation consistency issue |
| Originality | 10 | 8-10/10 — no existing issue covers this |
| Clarity | 5 | Depends on write-up |
| **Estimated total** | **100** | **58-74** |

## Verdict

**Real but minor finding.** Suitable as supplementary feedback in the Google Form, but NOT recommended as the primary Track 1 GitHub issue. See `05_SUBMISSION_STRATEGY.md` for the recommended primary issue.
