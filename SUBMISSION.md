# Cohort 3 Submission — Status

> **Resuming later?** Read [`context.md`](context.md) first, then run `python monitor.py`.

**Deadline:** 15 November 2026, 11:59 PM IST
**Results:** 23 November 2026
**Form:** https://docs.google.com/forms/d/1an-hce3EQ8bUVArnZJnD1VwxQIxgmNzLKYQ8h814CVE/viewform
**Form submitted:** 31 October 2026

---

## Track 1 — FILED

| | |
|---|---|
| **Issue** | [#346 — Material source coverage gate — pytest suites, test settings, and the testapp demo are counted as uncovered "production source files"](https://github.com/FinanceFlash/unvibecode/issues/346) |
| **URL** | https://github.com/FinanceFlash/unvibecode/issues/346 |
| **Repo** | `FinanceFlash/unvibecode` (upstream, not the fork) |
| **Author** | Cyberclutch146 |
| **State** | open |
| **PR created** | no (correct for Track 1) |

Duplicate check before filing: no existing issue. Searches for
`significant_production_source_files`, `24/55`, `43.6`, `test_settings.py`,
`testapp` + `coverage`, and `conftest.py` + `denominator` returned zero matches.
No issue by this account existed in the repository.

---

## Track 2 — copy into the form

Paste this into the Track 2 field:

```text
PR-native incremental review with a persistent .unvibe/ baseline

Approach. Move UnvibeCode's repeat unit from "run a full repository review" to
"review what this pull request changed." A developer runs `unvibe init` once;
afterwards every PR receives a branded, incremental review without anyone
remembering to run a CLI. `unvibecode diff --base origin/main` loads
`.unvibe/baseline.json`, takes the changed files, expands them one hop through the
existing resolved graph, and re-runs the gate and v4 selector only on that
subgraph. A GitHub Action upserts one sticky PR comment with changed workflows,
new or resolved findings, and the coverage delta.

Why it drives repeat usage. (1) A PR is exactly when impact analysis is needed, and
diff-scoped runs are cheap enough to run on every change - this also relieves the
hosted credit exhaustion I hit on a retry (#334). (2) The value is team-visible:
reviewers see the comment and the committed `.unvibe/context.md`, so the brand
stays in the repo and PR timeline instead of inside an invisible MCP call. (3) It
is feasible on today's engine - the graph, coverage gate, and selector already
exist, so diff mode is a filter and cache, not a new pipeline.

Plan. (1) Add `unvibecode diff --base <ref>` reusing the existing gate and selector
on a changed-file subgraph, cached to `.unvibe/baseline.json`. (2) Ship a GitHub
Action with one sticky comment, plus `unvibe init` to create the baseline.
(3) Instrument `diff_run`, `comment_posted`, and `finding_feedback`; target 30% of
onboarded repos running diff mode three weeks in a row.
```

Full and alternate versions: [`output/09_TRACK2_PROPOSAL.md`](output/09_TRACK2_PROPOSAL.md).

---

## Required feedback field (<200 words)

Rewrite this in your own voice before pasting — the form asks for human feedback.

```text
I ran UnvibeCode 0.3.15 on https://github.com/jazzband/django-payments at commit 5607e9e. The Connected Code Map and
Repository Context were fast and genuinely useful, and the business lane produced
three evidence-backed findings. Two things slowed me down: a retry of the business
run stopped with "hosted analysis credits exhausted", so I could not compare a
second repository; and on Windows the CLI raised UnicodeEncodeError before
rendering, so I had to set PYTHONUTF8=1. While validating the output I found that
the coverage gate counts pytest test_*.py, test_settings.py, and the testapp/ demo
as unrepresented "production source", reporting 43.6% instead of 59.3%.
Diff-scoped PR mode and clearer credit/retry handling would make repeat use much
easier.
```

Word count: 108.

---

## Optional five-word bonus (not required)

Pick one and only if it is your own:

- `Understand behavior, not just files.`
- `Trace workflows, verify real behavior.`
- `See the business inside code.`

---

## Form fields checklist

- [x] UnvibeCode 0.3.15 installed and run on a real public repository
- [x] Track 1 GitHub issue filed
- [x] Track 2 proposal written
- [x] Feedback draft written (<200 words)
- [x] Optional five-word options prepared
- [x] Name and email entered
- [x] Issue URL pasted: `https://github.com/FinanceFlash/unvibecode/issues/346`
- [x] Track 2 text pasted
- [x] Feedback pasted (rewritten in your own words)
- [x] Form submitted on 31 October 2026

The only step that cannot be automated from this machine is the Google Forms
submission, because it requires your Google account session.

A prefilled URL — email, issue link, Track 2 text, feedback, five-word line, and
confirmation — is stored in `FORM_PREFILL.local.txt`. That file is git-ignored
because it contains your email. Open it, review every field, rewrite the feedback
in your own voice, then submit.

---

## If you come back later

Run:

```powershell
python monitor.py
```

It reports, using public APIs only:

- whether #346 is still open, has labels, or has new comments (prints the latest one)
- whether PyPI has a release newer than **0.3.15**
- whether a newly filed issue matches the submission's keywords (known related issues from §9 are listed separately)
- the three newest commits on upstream `main`

Exit code `0` means nothing changed. Exit code `1` means something needs a look.

What to do if something changed:

| Change | Action |
|---|---|
| New maintainer comment on #346 | Reply within a day; stay technical; agree if they want to fold it into a broader fix |
| New UnvibeCode release | Run `python repro\repro_gate.py`; if output changed, comment on #346 with version and result |
| Another issue matches the keywords | Check whether it is genuinely the same denominator bug; comment or ask to consolidate |
| Issue closed as fixed | Run both repro scripts, confirm the fix, thank the maintainer |
| Results announced (23 Nov) | Check the challenge doc and your email |

## Reproduce the evidence

```powershell
python -m pip install "unvibecode==0.3.15"
python repro\repro_gate.py     # BUG REPRODUCED
python repro\repro_run.py "<work dir>\b\run"   # COUNTS MATCH
```

Details: [`repro/README.md`](repro/README.md).
