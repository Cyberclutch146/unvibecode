# Audit: Coverage Gate Denominator Bug — Primary Submission

## Status: ✅ RECOMMENDED PRIMARY SUBMISSION — Estimated 85-100/100

## Summary

The `significant_production_source_files()` function in the shipped UnvibeCode engine miscounts test files as production files. On `jazzband/django-payments`, it reports **24/55 (43.6%)** production coverage when the real figure is **16/27 (59.3%)** — a 15.6-point understatement. 20 of the 31 "uncovered production files" are actually pytest modules, test settings, a demo project, and Sphinx docs.

## Why This Is Your Strongest Finding

### 1. It's a WRONG ANSWER, not a missing feature

The function is named `significant_production_source_files()`. It returns test files. That's a wrong answer.

The Cohort 3 doc says: *"Finding a genuine defect is not the same as merely requesting a new feature."*

### 2. The downstream impact is traced end-to-end

```
significant_production_source_files()  [wrong filter]
    ↓
apply_repository_conclusion_gate()  [wrong ratio: 43.6% vs 59.3%]
    ↓
business_path_compiler_audit.jsonl  [wrong subjects, wrong reason]
    ↓
Step-4 candidates  [all get coverage_reliability: 1, confidence.coverage: 65]
    ↓
Model prompt  [qualification message with wrong file count]
    ↓
Final report  [PARTIAL_OR_UNKNOWN instead of potentially COMPLETE]
```

### 3. The controlled proof is devastating

§6.3 of the issue constructs a 6-file graph where **every production file is represented** (100% coverage). The function still reports:
- `significant_source_file_count: 5` (should be 2)
- `significant_uncovered_files: ['conftest.py', 'test_settings.py', 'testapp/manage.py']`
- `repository_wide_conclusions_allowed: False` (should be True)

A repository with perfect production coverage is told its conclusions are prohibited because test files aren't represented.

### 4. The root cause is precisely identified

`significant_production_source_files()` at line 3062-3066 uses a substring denylist:
```python
"/test/", "/tests/", "_test.", ".test.", ".spec.", "/fixtures/", "/examples/", "/demo/", "/samples/", "/generated/", "/vendor/", "node_modules/", "next-env.d.ts"
```

pytest names test modules with a **prefix** (`test_*.py`), not a suffix (`*_test.py`). The denylist has `_test.` but not `test_` as a basename prefix. Because the path is prefixed with `/` (line 3069: `lowered = f"/{file_path.casefold()}"`), a file like `payments/test_core.py` becomes `/payments/test_core.py` — the `test_` is preceded by `/`, not `_`.

### 5. It maps to Engineering Principles

| Principle | How the bug violates it |
|---|---|
| **Separation of Concerns** | Test-file classification (domain) is mixed with path-substring matching (infrastructure). Changing test layout changes the domain answer. |
| **Managing Complexity** | Three separate test-file filters in three modules use different criteria. They can drift apart. |
| **DDD / Clean Architecture** | The function named `significant_production_source_files()` doesn't deliver on its semantic contract. |

### 6. The duplicate check is exhaustive

7 related issues analyzed (#241, #50, #219, #238, #207, #201, #258, #148), all clearly distinct with different affected functions, outputs, and code paths.

## Cohort 3 Scoring Breakdown

| Criterion | Points | Assessment |
|---|---:|---|
| Technical depth, root-cause investigation | 35 | **30-35** — exact line identified, 4-stage downstream traced, three separate filters compared |
| Reproducibility and evidence | 30 | **27-30** — deterministic repro script against shipped code, §6.3 self-contained proof |
| Real developer impact | 20 | **16-20** — wrong production output, blocks valid conclusions, wrong info sent to model |
| Originality / non-duplicate | 10 | **8-10** — 7 issues checked, all distinct |
| Clarity | 5 | **4-5** — exact 9-section template, quantified impact |
| **TOTAL** | **100** | **85-100** |

## Location

The full issue text is at: `ISSUE_coverage_gate_test_files.md` (repository root)

## Pre-Filing Checklist

- [x] Confirm the TL;DR block and the version/hash proof in §2 are present
- [x] Run `repro/repro_gate.py` and `repro/repro_run.py` and confirm both pass
- [x] Re-check GitHub issues for duplicates on the filing date
- [x] Verify UnvibeCode has been installed and run
- [x] Filed at https://github.com/FinanceFlash/unvibecode/issues/346
- [ ] Submit Google Form with issue URL
