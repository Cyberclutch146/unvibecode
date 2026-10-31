# Track 2 — PR-Native Incremental Review with a Persistent `.unvibe/` Baseline

**Track:** 2 — Repeat-usage / adoption proposal
**Repo analyzed for context:** `jazzband/django-payments` @ `5607e9e` with UnvibeCode 0.3.15
**Submission field:** paste the "Form-ready text" section at the end

---

## The adoption problem

UnvibeCode is strong on the first run and weak on the second. A full review is
credit-expensive (I hit the hosted-credit wall on a retry — issue #334), it is manual,
and its output lives in a timestamped results folder that nobody on the team sees.
The result is a tool people try once, screenshot, and stop using.

The repeat unit today is "run a full repository review". It should be
"review what this pull request changed".

## Proposed approach

Move the repeat trigger into the pull request and keep a persistent baseline in the
repository.

1. **Diff-scoped analysis.** `unvibecode diff --base origin/main` loads
   `.unvibe/baseline.json`, takes the changed-file set, expands it one hop through the
   existing resolved connected-code graph, and re-runs the business-path compiler,
   coverage gate, and step-4 selection **only on that subgraph**.
2. **One sticky PR comment.** A GitHub Action runs on `pull_request`, upserts a single
   comment containing: changed workflows, new or resolved risk findings, the coverage
   delta, and a link to the full report. No comment spam on every push.
3. **A branded, committed baseline.** `unvibe init` writes `.unvibe/baseline.json` and
   `.unvibe/context.md` into the repo. The context file is human-readable and useful on
   its own, and a README badge is optional. The brand stays in the repository and in the
   PR timeline, not inside an invisible tool call.

## Three reasons this drives repeat usage

1. **The trigger is already in the developer's day.** A PR is exactly when someone needs
   impact analysis. Diff-scoped runs are far cheaper and faster than a full review, so
   the tool can run on every change instead of once per onboarding. This directly
   relieves the credit exhaustion documented in #334 and #329.
2. **The value is team-visible.** Reviewers see the comment without installing anything.
   `context.md` stays in the repo after the PR merges. Compare this with an MCP-only or
   editor-only integration, where the tool is invisible to the rest of the team and
   cannot show its value during code review.
3. **It is feasible on the existing engine.** The resolved graph, normalized business
   paths, coverage gate, and v4 selector already exist. Diff mode is a filter plus a
   cache over those artifacts, not a new analysis pipeline. That keeps the first version
   small enough to ship and instrument.

## Implementation plan (three steps)

1. **`unvibecode diff --base <ref>`.** Changed files → one-hop connected subgraph →
   reuse pass-1 artifacts → re-run gate and step 4 → persist results to
   `.unvibe/baseline.json`. Reuse the existing `significant_production_source_files()`,
   `apply_repository_conclusion_gate()`, and selector rather than duplicating logic.
2. **GitHub Action + `unvibe init`.** Action runs on `pull_request`, upserts one sticky
   comment via the issues API, fails soft when credits are unavailable, and posts a
   clear "analysis unavailable, retry" state instead of a silent gap. `unvibe init`
   creates the baseline and an optional README badge.
3. **Instrument and measure.** Anonymous events for `diff_run`, `comment_posted`, and
   `finding_feedback`. Measure weekly repeat runs per repository and the share of PRs
   that receive a comment. Success target: at least 30% of onboarded repositories run
   diff mode in three consecutive weeks, and at least 60% of diff-mode PR comments get a
   reviewer reaction or reply.

## Secondary entry point (optional, not the core)

`unvibe explain <file>` reads the same `.unvibe/baseline.json` inside OpenCode or an
editor. This is a convenience layer for individuals; the PR comment remains the repeat
trigger because it is visible to the whole team.

## Why this angle, and what was rejected

| Option | Why not primary |
|---|---|
| Pre-commit `unvibecode check --staged` | Already proposed by another participant (#312); narrow to one developer's machine |
| MCP-only / editor-only integration | The challenge explicitly warns against an invisible tool call; weak brand visibility and weak repeat signal |
| Generated workflow-invariant tests | Deeper, but high false-positive risk and a much longer build; better as a follow-up once diff mode stabilises |
| Full-review-only onboarding improvements | Does not change the repeat-use economics that caused credit exhaustion |

## Risks and mitigations

- **False positives in diff scope.** Start with "observe only" mode; the comment reports
  impact and findings without failing the check.
- **Credit unavailability.** Cache the baseline and render the last known state with an
  explicit stale marker, rather than dropping the comment.
- **Graph drift on large diffs.** Fall back to a full review when the changed set exceeds
  a configurable threshold; report why the fallback happened.

## Mapping to the challenge criteria

| Criterion | How this proposal scores |
|---|---|
| Repeat-usage potential (35) | PR trigger + cheap diff runs + committed baseline |
| Workflow fit (25) | Fits the existing review-before-merge habit |
| Feasibility (20) | Reuses graph, gate, and selector already shipped |
| Brand visibility (10) | Sticky comment header, `.unvibe/context.md`, optional badge |
| Clarity (10) | Concrete commands, artifacts, and metrics |

---

## Form-ready text (compact — recommended paste)

> **PR-native incremental review with a persistent `.unvibe/` baseline**
>
> **Approach.** Move UnvibeCode's repeat unit from "run a full repository review" to
> "review what this pull request changed." A developer runs `unvibe init` once; afterwards
> every PR receives a branded, incremental review without anyone remembering to run a CLI.
> `unvibecode diff --base origin/main` loads `.unvibe/baseline.json`, takes the changed
> files, expands them one hop through the existing resolved graph, and re-runs the gate and
> v4 selector only on that subgraph. A GitHub Action upserts one sticky PR comment with
> changed workflows, new or resolved findings, and the coverage delta.
>
> **Why it drives repeat usage.** (1) A PR is exactly when impact analysis is needed, and
> diff-scoped runs are cheap enough to run on every change — this also relieves the hosted
> credit exhaustion I hit on a retry (#334). (2) The value is team-visible: reviewers see
> the comment and the committed `.unvibe/context.md`, so the brand stays in the repo and
> PR timeline instead of inside an invisible MCP call. (3) It is feasible on today's
> engine — the graph, coverage gate, and selector already exist, so diff mode is a filter
> and cache, not a new pipeline.
>
> **Plan.** (1) Add `unvibecode diff --base <ref>` reusing the existing gate and selector
> on a changed-file subgraph, cached to `.unvibe/baseline.json`. (2) Ship a GitHub Action
> with one sticky comment, plus `unvibe init` to create the baseline. (3) Instrument
> `diff_run`, `comment_posted`, and `finding_feedback`; target 30% of onboarded repos
> running diff mode three weeks in a row.

---

## Form-ready text (full version — use if the field allows more depth)

> **Track 2 proposal — PR-native incremental review with a persistent `.unvibe/` baseline**
>
> UnvibeCode's repeat unit should move from "run a full repository review" to "review
> what this pull request changed." A developer runs `unvibe init` once; from then on
> every PR gets a branded, incremental review without anyone remembering to use a CLI.
>
> On each `pull_request`, `unvibecode diff --base origin/main` loads
> `.unvibe/baseline.json`, takes the changed files, expands them one hop through the
> existing resolved graph, and re-runs the business-path compiler, coverage gate, and
> step-4 selection only on that subgraph. A GitHub Action upserts one sticky comment
> with changed workflows, new or resolved findings, the coverage delta, and a report
> link, then refreshes `.unvibe/context.md` and `.unvibe/baseline.json`.
>
> Three reasons this increases repeat usage. First, a PR is exactly when impact analysis
> is needed, and diff-scoped runs are cheap enough to run on every change, which also
> relieves the hosted-credit exhaustion I hit on a retry (issue #334). Second, the value
> is team-visible: reviewers see the comment and the committed context file, so the
> brand stays in the repo and in the PR timeline rather than inside an invisible tool
> call. Third, it is feasible on the current engine: the resolved graph, normalized
> paths, coverage gate, and v4 selector already exist, so diff mode is a filter and cache
> over those artifacts, not a new pipeline.
>
> Implementation: (1) add `unvibecode diff --base <ref>` that reuses the existing gate
> and selector on a changed-file subgraph and caches to `.unvibe/baseline.json`;
> (2) ship a GitHub Action that upserts one sticky PR comment and add `unvibe init` to
> create the baseline; (3) instrument `diff_run`, `comment_posted`, and
> `finding_feedback` and measure weekly repeat runs per repo, targeting 30% of onboarded
> repos running diff mode for three consecutive weeks. An `unvibe explain <file>` command
> can reuse the same baseline in OpenCode as a secondary entry point, but the PR comment
> is the visible, repeatable trigger.
