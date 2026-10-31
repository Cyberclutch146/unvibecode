# [Bug] Guardrails checker — CI does not exercise the standalone CLI

> **Status: NOT SUBMITTED.** This is a secondary draft kept for reference. The Cohort 3
> submission is [`ISSUE_coverage_gate_test_files.md`](ISSUE_coverage_gate_test_files.md).

## 1. Problem summary

The repository distributes `guardrails_runner.py` as a standalone configuration-checking CLI, but the automated GitHub Actions workflow does not run behavioral tests against that module. The 13 regression tests in `04_common_guardrails_checker.ipynb` run against functions defined in the notebook kernel, including its local `main()`; they are not part of CI and do not import or launch the standalone runner.

This leaves the shipped CLI without automated regression coverage. A change can break CLI validation or exit-code behavior while the repository's CI remains green. The notebook also duplicates the checker implementation, so a fix or behavior change can be made in one copy without being applied to the other.

## 2. Test environment

- UnvibeCode version: **Not yet installed or run for this investigation. This field must be completed before using this report for Cohort 3 Track 1.**
- Operating system / Python version: Windows / Python 3.12.14 (Codex bundled runtime used for local inspection; confirm the participant's actual runtime before submission).
- Public repository URL and commit or release: Local checkout origin `https://github.com/Cyberclutch146/unvibecode`, commit `72b92916cf802e16b57ad868f7c68af451cf7f51`. The issue target appears to be the upstream UnvibeCode project, `https://github.com/FinanceFlash/unvibecode`; verify the exact analyzed public repository and revision after the required product trial.
- Relevant command: Source inspection and direct checker reproduction were performed. **The required Cohort 3 `python -m unvibecode review --repository ...` run has not been performed.** Add the exact install and review commands and the package version after completing that trial.

## 3. Steps to reproduce

1. Check out the repository revision under investigation.
2. Open `skills/unvibecode_gaurdrails_implemenataion_pack/Pre-configured_gaurdrails_programs/04_common_guardrails_checker.ipynb` and inspect its checker implementation cell and `ConfigurationTests` cell. The test methods call functions defined in the notebook; the CLI test calls the notebook-local `main()`.
3. Inspect `.github/workflows/test.yml`. Its pytest invocation is `python -m pytest -c .github/quality/pyproject.toml .github/quality/tests`.
4. Inspect `.github/quality/tests/test_repository_quality.py`: its tests validate repository documentation and workflow-pack quality, not guardrails runner behavior.
5. Confirm that no workflow step runs the notebook or a test module importing `guardrails_runner.py`.


## 4. Expected behavior

The normal CI workflow should run automated behavioral tests against the exact implementation users invoke through `guardrails_runner.py`. A green check should cover the CLI's configuration validation and user-visible command behavior, not only a parallel notebook copy.

The notebook may remain an educational, runnable example, but its implementation should have a defined source-of-truth relationship with the CLI so the two cannot silently diverge.

## 5. Actual behavior

The CI workflow runs pytest only against `.github/quality/tests`. It does not execute the notebook, import the runner, or invoke the runner CLI. The 13 notebook tests are manual and operate on notebook-defined functions. Thus CI currently does not detect regressions specific to the standalone runner, and notebook tests can pass independently of it.

## 6. Evidence

- `.github/workflows/test.yml:45-46`: the pytest step is restricted to `.github/quality/tests`.
- `.github/quality/tests/test_repository_quality.py:31-96`: tests cover workflow-pack structure, Markdown links, and repository documentation; no checker imports or calls are present.
- `skills/unvibecode_gaurdrails_implemenataion_pack/Pre-configured_gaurdrails_programs/04_common_guardrails_checker.ipynb`, code cell 2 and test cell 12: 13 test methods run against notebook-local functions. The CLI test calls notebook-local `main()` rather than subprocessing or importing the runner.
- `skills/unvibecode_gaurdrails_implemenataion_pack/Pre-configured_gaurdrails_programs/guardrails_runner.py:1, 286-307`: separate module documents the standalone CLI and defines the actual CLI entry point.
- `skills/unvibecode_gaurdrails_implemenataion_pack/Pre-configured_gaurdrails_programs/README_guardrails_checker.md:9-10`: describes the notebook and CLI as standalone deliverables and directs users to run the Python module.


## 7. Impact and scope

The affected users are contributors changing the common guardrails checker and users relying on its standalone CLI. A regression can escape the required CI checks, so maintainers may merge a change without automated evidence that the documented CLI still behaves as intended. A separate implementation in the notebook increases the chance of inconsistent behavior and makes it harder to know which tests protect the supported tool.

This finding is verified in the inspected repository checkout only. No claim is made that a downstream application is unsafe. The issue is a repository-level test architecture and regression-detection gap.

## 8. Suspected cause / suggested fix

The checker implementation and tests appear to have been maintained in the notebook, while a standalone CLI copy was added for terminal use. CI remained scoped to the repository-quality suite and was not connected to either checker implementation.

Suggested direction: make `guardrails_runner.py` the canonical checker module, move the behavioral tests into a conventional pytest module that imports it, and have the notebook demonstrate/import that module. If standalone notebook execution is a firm requirement, add a generation or parity check and still run behavioral tests against the CLI module in CI. Add a CLI-level test for the real entry point and exit codes.


## 9. Duplicate check

Preliminary searches of `FinanceFlash/unvibecode` on 26 October 2026 found no exact issue for the standalone guardrails checker's CI coverage. Related items to review before filing:

- [#151 — Quality tests silently pass if workflow pack directory is empty](https://github.com/FinanceFlash/unvibecode/issues/151) and [#116 — Validate required workflow-pack headings in quality tests](https://github.com/FinanceFlash/unvibecode/issues/116) concern repository-quality tests, but not the guardrails checker implementation or notebook/CLI divergence.
- [PR #189 — Add practical guardrails notebooks and configuration checker](https://github.com/FinanceFlash/unvibecode/pull/189) introduced the checker. Its verification notes 13 checker tests were rerun but says the full repository quality suite and interactive notebook were not run. This is relevant background; the present report concerns connecting behavior tests to CI and the standalone module, which PR #189 did not claim to do.
- [#129 — Review Tool Feedback - Windows Path / Run Execution](https://github.com/FinanceFlash/unvibecode/issues/129) concerns handling an empty repository path, a different CLI behavior.

Searches included `guardrails`, `guardrails_runner`, `checker`, `notebook`, `CI tests`, and `quality tests`. Repeat the open/closed issue and PR search immediately before filing and check whether the maintainer has since added CI coverage.

## Cohort 3 Track 1 submission status

This draft is **not ready to submit yet**. Cohort 3 requires installing and running UnvibeCode on a real public repository, verifying the output against source, and filing one original, non-duplicate issue using the challenge template. The repository evidence above came from direct source inspection and a checker reproduction; the required UnvibeCode product trial has not been performed. Complete section 2 with the real trial details, assess whether the trial supports this issue, and repeat the duplicate check before creating an issue. Do not submit a pull request for Track 1.


