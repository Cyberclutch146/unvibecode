# 🏆 Cohort 3 Submission Guide — Both Tracks

## Overview

| Item | Value |
|---|---|
| **Deadline** | 15 November 2026, 11:59 PM IST |
| **Results** | 23 November 2026 |
| **Tracks** | Track 1 (GitHub issue) **and** Track 2 (written adoption proposal) |
| **Form** | https://docs.google.com/forms/d/1an-hce3EQ8bUVArnZJnD1VwxQIxgmNzLKYQ8h814CVE/viewform |
| **Track 1 issue** | [#346](https://github.com/FinanceFlash/unvibecode/issues/346) — **filed**, open |

Both tracks require you to install and run UnvibeCode on a real public repository.
Only Track 1 requires a GitHub issue. Track 1 has **no pull request**.

---

## Step 1: Install UnvibeCode (required)

```powershell
python -m pip install --upgrade "unvibecode==0.3.15"
python -m unvibecode --help
```

Record the version. The issue documents **0.3.15**, the latest PyPI release as of
31 October 2026, with engine SHA-256
`b98412a824acd0872b05ea3b83d7b663f441db201c080b821dbd54917ef77387`.

---

## Step 2: Run UnvibeCode on a public repository (required)

Use the repo that backs the issue, so the submission and the run agree.

```powershell
git clone https://github.com/jazzband/django-payments
cd django-payments
git checkout 5607e9e88762df9831980832c194f49b227dbe93
cd ..

# Windows: avoid the cp1252 UnicodeEncodeError (issue #335)
$env:PYTHONUTF8 = "1"

python -m unvibecode review --repository "C:\path\to\django-payments" --no-open-browser
```

Any real public repository is acceptable, but django-payments is the one cited in
the issue and the one with retained evidence.

### What to inspect

- **Business Workflow Map** — does it match the actual code?
- **Connected Code Map** — are the edges accurate?
- **Business Risk Findings** — are they evidence-backed?
- **Complete Repository Context / coverage** — is the denominator right?

Save the output directory (`unvibecode_results/<name>-unvibecode-analysis-YYYYMMDD_HHMMSS`)
and the work-dir path from `technical-logs/recovery-location.txt`.

---

## Step 3: Track 1 — the coverage-gate issue

Primary artifact: [`ISSUE_coverage_gate_test_files.md`](../ISSUE_coverage_gate_test_files.md).

It follows the required 9-section template:

```markdown
Title: [Bug] <component> — <specific observable failure>

## 1. Problem summary
## 2. Test environment
## 3. Steps to reproduce
## 4. Expected behavior
## 5. Actual behavior
## 6. Evidence
## 7. Impact and scope
## 8. Suspected cause / suggested fix (if known)
## 9. Duplicate check
```

### 3a. Re-run the proofs before filing

From the repo root, with the 0.3.15 environment active:

```powershell
python repro\repro_gate.py
```

Expected: `2/5`, ratio `0.4`, `allowed: False`, `BUG REPRODUCED`.

If you still have the run artifacts:

```powershell
python repro\repro_run.py "C:\path\to\uvc-xxxx\b\run"
```

Expected: `55 24 31` then `27 16 11`, `COUNTS MATCH`.

Neither script spends hosted analysis credits. See [`repro/README.md`](../repro/README.md).

### 3b. Re-check for duplicates

Search https://github.com/FinanceFlash/unvibecode/issues for:

- `significant production source files`
- `material source coverage`
- `coverage gate`
- `significant_source_file_count`
- `test_*.py`
- `testapp`
- `conftest`
- `denominator`

Last sweep: 31 October 2026. No duplicate. Closest are **#50** (enforcing the gate,
not counting its inputs), **#241** (Ruby RSpec files in structural review), and
**#331** (a `conftest.py` symbol edge, unrelated to the denominator). §9 of the issue
explains each distinction.

### 3c. File it

**Filed:** https://github.com/FinanceFlash/unvibecode/issues/346 (open, by Cyberclutch146).

The steps below are kept for reference or if the issue ever needs to be re-filed.

1. Go to https://github.com/FinanceFlash/unvibecode/issues/new
2. Copy the **whole** contents of `ISSUE_coverage_gate_test_files.md`
3. Title: `[Bug] Material source coverage gate — pytest suites, test settings, and the testapp demo are counted as uncovered "production source files"`
4. Check the preview: code blocks, tables, and the `> TL;DR` block
5. Submit, then copy the issue URL

> ⚠️ **No pull request.** Track 1 is issue-only.

---

## Step 4: Track 2 — adoption proposal

Full text: [`09_TRACK2_PROPOSAL.md`](09_TRACK2_PROPOSAL.md).

The proposal is **PR-native incremental review with a persistent `.unvibe/` baseline**:

- `unvibecode diff --base origin/main` reviews only the changed files plus one hop
  of the connected graph.
- A GitHub Action upserts one sticky PR comment with workflow impact, new findings,
  and the coverage delta.
- `.unvibe/baseline.json` and `.unvibe/context.md` are committed, so repeat runs are
  incremental and cheap.
- This also addresses the credit exhaustion observed in issue #334.

Paste it into the Track 2 field. 2–3 supporting points and a 2–3 step plan are
already structured in the file.

---

## Step 5: Fill the Google Form

https://docs.google.com/forms/d/1an-hce3EQ8bUVArnZJnD1VwxQIxgmNzLKYQ8h814CVE/viewform

| Field | What to enter |
|---|---|
| Name / team | Your name |
| Email | Your email |
| **Brief UnvibeCode feedback (<200 words, required)** | Use the draft in §5a below — rewrite it in your own voice |
| GitHub issue link (Track 1) | The URL from Step 3c |
| Track 2 proposal | Paste `09_TRACK2_PROPOSAL.md` |
| Five-word punchline | **Optional bonus**, not required — see §5b |
| Confirmation | Tick it |
| GitHub profile | Optional |
| College / year | Optional |
| Referral | Optional |

### 5a. Draft feedback (<200 words)

> I ran UnvibeCode 0.3.15 on django-payments at `5607e9e`. The Connected Code Map and
> Repository Context were fast and genuinely useful, and the business lane produced
> three evidence-backed findings. Two things slowed me down: a retry of the business
> run stopped with "hosted analysis credits exhausted", so I could not compare a second
> repository; and on Windows the CLI raised `UnicodeEncodeError` before rendering, so I
> had to set `PYTHONUTF8=1`. While validating the output I found that the coverage gate
> counts pytest `test_*.py`, `test_settings.py`, and the `testapp/` demo as unrepresented
> "production source", reporting 43.6% instead of 59.3%. Diff-scoped PR mode and clearer
> credit/retry handling would make repeat use much easier.

Rewrite this so it reads as your own words. The form explicitly asks for human feedback,
not AI-written text.

### 5b. Optional five-word punchline

Only if you want the bonus. Exactly five words, original:

- `Understand behavior, not just files.`
- `Trace workflows, verify real behavior.`
- `See the business inside code.`

---

## Step 6: Pre-submit checklist

- [ ] UnvibeCode 0.3.15 installed and run on a real public repository
- [ ] `repro_gate.py` prints `BUG REPRODUCED`
- [ ] Output reviewed against the actual source
- [x] Issue filed with the 9-section template on `FinanceFlash/unvibecode`
- [x] Issue title starts with `[Bug]`
- [ ] Duplicate sweep re-run on the filing date and §9 date updated
- [ ] No pull request created
- [ ] Track 2 proposal pasted
- [ ] Feedback field under 200 words and written in your own voice
- [ ] Five-word line left blank or exactly five words
- [ ] No private data, credentials, customer info, or private repo content
- [ ] UnvibeCode repo starred
- [ ] Form submitted before 15 November 2026, 11:59 PM IST

---

## Timeline

| When | What |
|---|---|
| Now | Run `repro/` scripts, re-check duplicates |
| **Done 31 Oct** | Issue filed: https://github.com/FinanceFlash/unvibecode/issues/346 |
| 1–5 Nov | Finalise Track 2 text and the feedback paragraph |
| 6–10 Nov | Re-verify against any new release; update version proof if needed |
| Before 15 Nov | Submit the form — do not wait for the deadline |

---

## Scoring reminder (Track 1, 100 points)

| Criterion | Points | Strength |
|---|---:|---|
| Technical depth, root cause, reasoning | 35 | Root cause at exact lines; 4-stage downstream impact |
| Reproducibility and evidence | 30 | Self-contained 6-file repro + run-specific 55/24/31 |
| Real developer impact | 20 | Wrong coverage answer that changes the qualification |
| Originality / non-duplicate scope | 10 | Live sweep; 8 related issues distinguished |
| Clarity | 5 | Exact 9-section template |

Track 2 is scored mainly on repeat-usage potential and workflow fit, which is why the
PR-native angle was chosen.

---

## Files

| File | Contents |
|---|---|
| `SUBMISSION.md` | Live status, issue URL, and copy-paste form text (repo root) |
| `ISSUE_coverage_gate_test_files.md` | Track 1 issue (repo root) |
| `repro/repro_gate.py` | Self-contained proof; wheel only |
| `repro/repro_run.py` | Run-specific `55/24/31` and `27/16/11` |
| `repro/README.md` | Install and expected output |
| `output/09_TRACK2_PROPOSAL.md` | Track 2 submission text |
| `output/05_SUBMISSION_STRATEGY.md` | Finding comparison |
| `output/07_AUDIT_PRIMARY_SUBMISSION_COVERAGE_GATE.md` | Scoring rationale |
| `output/01`–`04` | Adversarial audits of the candidates |
| `ISSUE_guardrails_checker_test_coverage.md` | Secondary draft, not submitted |

---

## Key URLs

- Challenge doc: https://github.com/FinanceFlash/unvibecode/blob/main/docs/UnvibeCode_Engineering_Challenge_2026_Cohort_3.md
- File an issue: https://github.com/FinanceFlash/unvibecode/issues/new
- Existing issues: https://github.com/FinanceFlash/unvibecode/issues
- Google Form: https://docs.google.com/forms/d/1an-hce3EQ8bUVArnZJnD1VwxQIxgmNzLKYQ8h814CVE/viewform
- Star the repo: https://github.com/FinanceFlash/unvibecode
