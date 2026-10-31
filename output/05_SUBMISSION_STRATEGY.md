# Submission Strategy & Comparison

## The Ranking

| Rank | Finding | Est. Score | Type | File |
|---|---|---:|---|---|
| 🥇 | **Coverage gate denominator bug** | 85-100 | Code defect — wrong answer | `ISSUE_coverage_gate_test_files.md` |
| 🥈 | Duplicate-value validation gap | 58-74 | Validation gap — low impact | `03_AUDIT_CANDIDATE2_DUPLICATE_VALUES.md` |
| 🥉 | CI test coverage gap | 51-67 | Process observation | `04_AUDIT_CANDIDATE3_CI_GAP.md` |

## Why the Coverage Gate Bug Wins

### It scores highest on EVERY Cohort 3 criterion

| Criterion (Points) | Coverage Gate Bug | Duplicate Values | CI Gap |
|---|---|---|---|
| **Technical depth (35)** | 30-35 — root cause traced to exact line, downstream impact mapped through 4 pipeline stages | 18-23 — straightforward missing check | 15-20 — grep-level observation |
| **Reproducibility (30)** | 27-30 — deterministic script, §6.3 self-contained proof | 22-27 — 3-line repro | 20-25 — inspect YAML file |
| **Real impact (20)** | 16-20 — wrong answer in production output, blocks valid conclusions | 10-14 — validation consistency | 8-12 — process suggestion |
| **Originality (10)** | 8-10 — 7 related issues checked, all distinct | 8-10 — novel | 8-10 — novel |
| **Clarity (5)** | 4-5 — follows exact 9-section template | 4-5 | 4-5 |

### It's the right TYPE of finding

The Cohort 3 doc says:
> "Depth matters more than issue count. One thoroughly investigated, reproducible, high-impact issue can make a stronger case. **Finding a genuine defect is not the same as merely requesting a new feature.**"

- Coverage gate bug = **genuine defect** (wrong answer: 43.6% instead of 59.3%)
- Duplicate values = defect (minor)
- CI gap = **feature request** (add tests to CI)

### It demonstrates end-to-end engineering reasoning

The coverage gate issue traces the bug through:
1. **Input:** `significant_production_source_files()` — wrong filter
2. **Gate:** `apply_repository_conclusion_gate()` — wrong ratio and decision
3. **Compiler:** audit record with wrong subjects and reason
4. **Candidates:** every step-4 candidate gets `coverage_reliability: 1` and `confidence.coverage: 65`
5. **Model prompt:** qualification message with wrong file count sent to LLM
6. **Controlled proof:** §6.3 shows 100% production coverage reported as 40%

This maps to Engineering Principle #1 (Separation of Concerns) — the test-file classification is a concern that should be separated cleanly, but three different filters in three different modules use different criteria.

## What to Submit Where

### GitHub Issue (ONE issue only)
→ Submit: **Coverage gate denominator bug** (`ISSUE_coverage_gate_test_files.md`)

### Google Form — "Brief feedback" field (<200 words, required)

Use the draft in `06_CHALLENGE_GUIDE.md` §5a and rewrite it in your own voice. Keep
the duplicate-value finding out of the form: the field is a short human-feedback box,
and it is stronger focused on the run you actually submitted.

### Google Form — "Five-word explanation" (optional bonus)

Only if you want the bonus, and only if the line is exactly five words and your own:

- "Trace workflows, verify business logic"
- "Understand code beyond surface reading"
- "Map business paths through code"

The form marks this as optional. Do not let it delay the submission.
