# Audit: Candidate 3 — CI Test Coverage Gap for `guardrails_runner.py`

## Status: ✅ CONFIRMED — Genuine Infrastructure Gap

## Claim

The `guardrails_runner.py` checker has 13 regression tests in `04_common_guardrails_checker.ipynb`, but the CI pipeline (`test.yml`) only runs pytest on `.github/quality/tests/`. The guardrails checker tests never execute in CI.

## Evidence

### CI Pipeline (test.yml, lines 45-46)
```yaml
- name: Run repository-quality tests
  run: python -m pytest -c .github/quality/pyproject.toml .github/quality/tests
```
Scope: **ONLY** `.github/quality/tests/`

### What `.github/quality/tests/test_repository_quality.py` actually tests
- Workflow pack file presence (line 36-38)
- MECE boundary definitions (line 42-47)
- Core scenario counts (line 51-54)
- Skill frontmatter (line 58-64)
- Pack index links (line 67-70)
- GitHub automation file locations (line 73-85)
- Markdown encoding (line 88-92)
- Local markdown link resolution (line 95-107)

**Zero imports of `guardrails_runner`**. Zero tests of Python validation logic.

### What `guardrails_runner.py` contains
- 307 lines of executable Python
- `make_profile()` — profile generation for 4 application types
- `check()` — 130+ lines of validation logic with 30+ error codes
- `fingerprint()` — SHA-256 configuration hashing
- `read_config()` — JSON parsing with duplicate-key rejection
- `questions()` — context-aware design question generation
- `main()` — CLI entry point with `init`, `check`, `questions` subcommands

### What the 13 notebook tests cover
- Profile generation for all 4 application types
- Required control sets per application
- Feature flag enforcement (RAG→retrieval, agent→tools)
- Anti-pattern detection (fail-open, late checks, wrong stage, etc.)
- CLI exit codes (0 for valid, 1 for invalid, 2 for parse errors)
- JSON parsing edge cases (duplicate keys, non-finite numbers)
- Schema validation (missing/unknown keys)

### CONTRIBUTING.md confirmation (line 46-48)
> "The test suite verifies local Markdown links, workflow-pack structure, core scenario counts, workflow boundaries, and LLM skill metadata."

No mention of guardrails checker tests.

## Counter-Arguments Addressed

| Counter-Argument | Rebuttal |
|---|---|
| "The notebook is designed for manual use" | True, but a PR modifying `guardrails_runner.py` shows green CI even if it breaks validation. That's a regression risk. |
| "The checker is standalone, not part of core" | It's in the repo, referenced by the README, maintained alongside the code. CI already covers quality — just not this module. |
| "Notebook tests are thorough enough" | Thoroughness without automation = stale tests if code evolves without re-running the notebook. |

## Suggested Fix

1. Extract the 13 `unittest.TestCase` methods from the notebook into a pytest-compatible module (e.g., `tests/test_guardrails_runner.py`)
2. Add `import guardrails_runner` to test against the shipped CLI module (not notebook-local copies)
3. Add the test directory to the CI pytest invocation in `test.yml`
4. Optionally: add a notebook-parity check to ensure the notebook copy stays in sync

## Engineering Principles Alignment

| Principle | Violation |
|---|---|
| **Managing Complexity** | Three separate code surfaces exist (notebook implementation, standalone module, CI tests) with no connection between the testable module and CI. |
| **Separation of Concerns** | The CI pipeline's concern is quality verification, but it doesn't cover the only executable Python utility in the repository. |

## Cohort 3 Scoring Assessment

| Criterion | Points | Assessment |
|---|---:|---|
| Technical depth | 35 | 15-20/35 — primarily an observation; grep-level finding |
| Reproducibility | 30 | 20-25/30 — deterministic (inspect test.yml, confirm no guardrails imports) |
| Real developer impact | 20 | 8-12/20 — process suggestion, not a code defect |
| Originality | 10 | 8-10/10 — no existing issue covers this |
| Clarity | 5 | 4-5/5 — existing draft is well-structured |
| **Estimated total** | **100** | **51-67** |

> **Important:** The Cohort 3 challenge doc says "Finding a genuine defect is not the same as merely requesting a new feature." This finding is closer to a process improvement request than a code defect, which weakens it for Track 1.

## Verdict

**Genuine but weak for Track 1 submission.** This is a real infrastructure gap, but it's a process observation rather than a code defect. Not recommended as the primary GitHub issue. See `05_SUBMISSION_STRATEGY.md`.
