# CONTEXT — UnvibeCode Cohort 3 submission

Read this first when resuming. It is the single source of truth for what was
submitted, what was verified, and what is left.

Last updated: 31 October 2026.

---

## 1. The challenge

**UnvibeCode Engineering Challenge 2026 — Cohort 3**

| Item | Value |
|---|---|
| Deadline | 15 November 2026, 11:59 PM IST |
| Results | 23 November 2026 |
| Submission form | https://docs.google.com/forms/d/1an-hce3EQ8bUVArnZJnD1VwxQIxgmNzLKYQ8h814CVE/viewform |
| Challenge doc | https://github.com/FinanceFlash/unvibecode/blob/main/docs/UnvibeCode_Engineering_Challenge_2026_Cohort_3.md |
| Upstream repo | `FinanceFlash/unvibecode` |
| Fork | `Cyberclutch146/unvibecode` |

Two tracks, both submitted:

- **Track 1** — one original, non-duplicate GitHub issue. No PR.
- **Track 2** — written adoption / repeat-usage proposal, pasted into the form.

## 2. Status

| Item | State |
|---|---|
| Track 1 issue | **Filed and open:** https://github.com/FinanceFlash/unvibecode/issues/346 |
| Issue author | `Cyberclutch146` |
| Issue created | 2026-10-31T07:30:52Z |
| Comments / labels | 0 / 0 as of last check |
| Track 2 proposal | Written; pasted into the form |
| Google Form | **Submitted 31 October 2026** |
| Latest PyPI release | 0.3.15 (unchanged since 2026-10-23) |

## 3. Track 1 — what the issue says

**Title:** `[Bug] Material source coverage gate — pytest suites, test settings, and the testapp demo are counted as uncovered "production source files"`

**Finding:** `significant_production_source_files()` excludes test scaffolding with a
substring denylist (`/test/`, `/tests/`, `_test.`, `.test.`, ...) that misses pytest's
default `test_*.py` prefix, `test_settings.py`, `conftest.py`, and a `testapp/` demo.
The repository conclusion gate therefore uses a wrong denominator.

**Repository analyzed:** https://github.com/jazzband/django-payments @
`5607e9e88762df9831980832c194f49b227dbe93` (2026-10-10).

**Observed on that run:**

| Metric | Reported | Correct (production only) |
|---|---:|---:|
| Significant source files | 55 | 27 |
| Represented | 24 | 16 |
| Uncovered | 31 | 11 |
| Coverage | 43.6% | 59.3% |

20 of the 31 "unrepresented production files" are tests, the demo app, or Sphinx docs.
The gate sets `repository_wide_conclusions_allowed = false` and injects
`material_source_coverage: PARTIAL_OR_UNKNOWN` into every candidate.

**Controlled proof:** a six-file graph where all production files are represented still
reports `5 / 2 / 0.4 / allowed=False`.

**Root cause:** `shipreadyv2/engine_sources/04_shipreadyv2_business_path_compiler.py`,
`significant_production_source_files()` at lines 3056-3077. `lowered` is prefixed with
`/` at line 3069, so `_test.` can never match a `test_*.py` basename.

**Suggested fix:** one shared `is_test_or_demo_path()` predicate used by
`significant_production_source_files()`, `derive_reachability()` (same file, 1562-1563),
and `STRUCTURAL_EXCLUDED_PATH_PARTS` (`06_...step4_v2_with_v4_inputs.py:398-402`).
Do not key it off pytest `testpaths`, which here names the whole package.

## 4. Track 2 — what was proposed

**PR-native incremental review with a persistent `.unvibe/` baseline.**

- `unvibecode diff --base origin/main` reviews changed files plus one hop of the graph.
- A GitHub Action upserts one sticky PR comment with workflow impact and coverage delta.
- `.unvibe/baseline.json` and `.unvibe/context.md` are committed, so repeat runs are cheap.
- Rationale: a PR is the natural repeat trigger; the value is team-visible; it is feasible
  on the current engine; and it relieves the credit exhaustion seen in issue #334.

Full text: `output/09_TRACK2_PROPOSAL.md`. Form-ready copy: `SUBMISSION.md`.

## 5. Verified evidence

Environment: UnvibeCode **0.3.15**, Windows 11 **10.0.26200**, Python **3.12.5**.
Engine SHA-256: `b98412a824acd0872b05ea3b83d7b663f441db201c080b821dbd54917ef77387`.

```powershell
python repro\repro_gate.py
# production files represented: 2/2 (100%)
# significant_source_file_count: 5
# represented_significant_source_file_count: 2
# significant_source_coverage_ratio: 0.4
# significant_uncovered_files: ['conftest.py', 'test_settings.py', 'testapp/manage.py']
# repository_wide_conclusions_allowed: False
# BUG REPRODUCED

python repro\repro_run.py "<work dir>\b\run"
# 55 24 31
# 27 16 11
# COUNTS MATCH
```

The run artifacts used for `repro_run.py` were at:

```
%LOCALAPPDATA%\Temp\uvc-hd0g1m3c\b\run
```

Run id: `target-unvibecode-analysis-20261026_150012`. Temporary files may be cleaned by
Windows; `repro_gate.py` does not depend on them and is the durable proof.

## 6. Duplicate check

Live checks on 31 October 2026 found no duplicate. Searches for
`significant_production_source_files`, `24/55`, `43.6`, `test_settings.py`,
`testapp` + `coverage`, and `conftest.py` + `denominator` returned only #346 itself
(or nothing). No issue by this account existed before #346.

Known related issues, all distinguished in §9 of the issue:

| Issue | Why it is not this bug |
|---|---|
| #50 | Enforces the gate at report/terminal boundary; takes the counts as given |
| #241 | Ruby `spec/` files in structural review; different function and output |
| #331 | `conftest.py` resolved as an import target in the Connected Code Map |
| #238, #219 | How test files are labelled after they enter reachability / evidence |
| #207, #201 | Example/test workflows presented as core business workflows |
| #258 | Pytest fixtures resolved as import symbols |
| #148 | Directory filters hiding source, not over-counting tests as production |

## 7. Files

| Path | Purpose |
|---|---|
| `context.md` | This resume file |
| `SUBMISSION.md` | Submission status, issue URL, copy-paste form text |
| `ISSUE_coverage_gate_test_files.md` | Exact Track 1 issue text (filed as #346) |
| `repro/repro_gate.py` | Self-contained proof; wheel only |
| `repro/repro_run.py` | Run-specific `55/24/31` and `27/16/11` |
| `repro/README.md` | Install and expected output |
| `output/09_TRACK2_PROPOSAL.md` | Track 2 full proposal |
| `output/05_SUBMISSION_STRATEGY.md` | Why this finding was chosen |
| `output/06_CHALLENGE_GUIDE.md` | Step-by-step submission guide |
| `output/07_AUDIT_PRIMARY_SUBMISSION_COVERAGE_GATE.md` | Scoring rationale and checklist |
| `output/01`–`04` | Audits of the three candidate findings |
| `monitor.py` | Checks issue, PyPI, duplicates, upstream commits |
| `ISSUE_guardrails_checker_test_coverage.md` | Secondary draft, **not submitted** |
| `FORM_PREFILL.local.txt` | Prefilled form URL; git-ignored because it contains the email |

## 8. Rules and gotchas

- **Do not open a pull request for Track 1.** The challenge explicitly prohibits it.
- **Do not commit `FORM_PREFILL.local.txt`.** It contains a personal email. It is git-ignored.
- **Feedback on the form was supposed to be rewritten in the submitter's own words.**
  The form asks for human feedback, not AI text.
- The issue title must stay in the form `[Bug] <component> — <failure>`. It does.
- The five-word line is optional bonus, not required.
- Track 1 scores on technical depth (35), reproducibility (30), impact (20),
  originality (10), clarity (5).
- Track 2 scores on repeat usage (35), workflow fit (25), feasibility (20),
  brand recall (10), reasoning (10).

## 9. How to resume

```powershell
cd %USERPROFILE%\Downloads\unvibecode
python monitor.py
```

It reports:

- #346 state, labels, comment count, and the latest comment
- whether PyPI has a release newer than 0.3.15
- any newly filed issue matching the submission keywords (known related list excluded)
- the three newest upstream commits

Exit `0` = nothing changed. Exit `1` = something needs attention.

| Change | Action |
|---|---|
| New maintainer comment | Reply within a day; stay technical; accept a broader fix gracefully |
| New release | Run `python repro\repro_gate.py`; if output changed, comment on #346 with version and result |
| New matching issue | Decide if it is the same denominator bug; comment or ask to consolidate |
| Issue closed as fixed | Re-run both repro scripts, confirm, thank the maintainer |
| Results announced | 23 November 2026; check email and the challenge doc |

## 10. Repo state

Fork: https://github.com/Cyberclutch146/unvibecode

All submission work is committed and pushed to `main`. Check the exact head with:

```powershell
git -C %USERPROFILE%\Downloads\unvibecode log --oneline -10
```

Nothing is pending except monitoring.
