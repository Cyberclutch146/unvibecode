# [Bug] Material source coverage gate — pytest suites, test settings, and the testapp demo are counted as uncovered "production source files"

> **TL;DR:** `significant_production_source_files()` admits pytest's `test_*.py`, `test_settings.py`, `testapp/`, and `conftest.py` as production source. On django-payments it reports 24/55 (43.6%) instead of 16/27 (59.3%), and the gate prohibits repository-wide conclusions. A self-contained six-file repro reports 100% production coverage as 40%.

## 1. Problem summary

The repository conclusion gate builds its denominator with `significant_production_source_files()`, which excludes test scaffolding by matching a short list of path substrings. That list recognises `/test/`, `/tests/`, `_test.` and `.test.`, but not Python's pytest conventions (`test_*.py`), nor `test_settings.py`, `conftest.py`, or a `testapp/` demo project.

On `jazzband/django-payments` — a repository whose tests live inside the package, as its own `pyproject.toml` configures — 28 of the 55 files counted as production source are pytest modules, test settings, the demo project, and the Sphinx config. The gate therefore reports **24/55 (43.6%)** when production coverage is **16/27 (59.3%)**, and states that *"31 significant production source files are not represented"* when 20 of those 31 are not production source at all.

This is not just a cosmetic label. The wrong denominator is written to `business_path_coverage.json` and the compiler audit, injected into every step-4 candidate as `material_source_coverage: PARTIAL_OR_UNKNOWN`, and it lowers each candidate's score (`coverage_reliability: 1/2`, `confidence.coverage: 65/90`). When a repository's production files are fully represented but its tests are not, the gate returns `repository_wide_conclusions_allowed: false` and prohibits repository-wide absence conclusions for no valid reason; the shipped function reproduces this on a six-file input (§6.3).

## 2. Test environment

- **UnvibeCode version:** 0.3.15 (PyPI wheel; the `shipreadyv2` engine is bundled inside the wheel)
  - 0.3.15 is the latest release on PyPI as of 31 October 2026. The bundled `engine_sources/04_shipreadyv2_business_path_compiler.py` has SHA-256 `b98412a824acd0872b05ea3b83d7b663f441db201c080b821dbd54917ef77387` in the Windows wheels, and `significant_production_source_files()` is unchanged.
- **Operating system / Python:** Windows 11 (10.0.26200), Python 3.12.5 (CPython, MSC v.1940, 64-bit)
- **Public repository:** https://github.com/jazzband/django-payments @ `5607e9e88762df9831980832c194f49b227dbe93` (2026-10-10, *"sagepay: fix crash due to type inconsistency"*)
- **Command:** `python -m unvibecode review --repository "C:\...\django-payments" --no-open-browser`
  On Windows, `PYTHONUTF8=1` was set to avoid an unrelated console-encoding crash that occurs before the dashboard renders; that crash is not part of this report.
- **Run:** `unvibecode_results/target-unvibecode-analysis-20261026_150012`. The business lane completed (`Published flaws: 3`); all artifacts quoted below were produced by that lane.

## 3. Steps to reproduce

1. `git clone https://github.com/jazzband/django-payments && git checkout 5607e9e88762df9831980832c194f49b227dbe93`, create a Python 3.12 virtualenv, and `pip install unvibecode==0.3.15`.
2. Run `python -m unvibecode review --repository "<path>" --no-open-browser` (prefix with `PYTHONUTF8=1` on Windows).
3. Open `<analysis dir>/technical-logs/recovery-location.txt`, then the working directory it names:
   - `<work dir>/b/run/business_path_coverage.json` → `scan.qualification_message` and `coverage.coverage_warnings`
   - `<work dir>/b/run/business_path_compiler_audit.jsonl` → the `REPOSITORY_CONCLUSION_GATE` record
   - `<work dir>/b/run/shipreadyv2_customer_business_flaw_report_v2_run_001.json` → `repository.coverage_warnings`
4. To verify the decision impact without any analysis run or credits, use the self-contained snippet in §6.3. For the run-specific counts, §6.4 loads the shipped classifier and the run's `shipreadyv2_resolved_graph.json` and prints `55 / 24 / 31`, then the production-only `27 / 16 / 11`.

The classification is a pure function of the graph node list, so step 4 is deterministic and needs no second review. Observed once end-to-end (1/1); the end-to-end run was not repeated because the hosted analysis service returned *API credits exhausted* on the retry.

## 4. Expected behavior

Only production source should enter the denominator; the gate's own warning and audit record call these files *"significant production source files"*.

Three separate places already try to keep test surfaces out of production analysis:

- `significant_production_source_files()` here (`04_shipreadyv2_business_path_compiler.py:3056-3077`).
- `derive_reachability()` in the same module classifies a path containing `/test/`, `/tests/`, `_test.`, `.test.`, `fixture`, `example/`, `demo/`, `sample/` as `TEST_DEMO_SAMPLE` (`04_shipreadyv2_business_path_compiler.py:1562-1563`).
- The structural-review filter excludes the same path conventions (`06_shipreadyv2_step4_v2_with_v4_inputs.py:398-402`, `STRUCTURAL_EXCLUDED_PATH_PARTS`).

All three use the same substring list, so all three miss pytest's default `test_*.py` naming, `test_settings.py`, `testapp/`, and a root `conftest.py`. That shared blind spot is evidence of an intended policy — and of why one shared predicate is the right fix — not evidence that the product already handles these conventions correctly.

The function's own name is also part of the contract: it is called `significant_production_source_files`, and the warning it emits says *"significant source files"* while the qualification message says *"significant **production** source files"*.

The analysed repository also states its own test layout explicitly:

- `pyproject.toml:76-85` — `[tool.pytest.ini_options]`, `testpaths = "payments"`, `DJANGO_SETTINGS_MODULE = "test_settings"`; dev extras include `pytest`, `pytest-cov`, `pytest-django` (`pyproject.toml:41-53`).
- `tox.ini:28` runs `pytest`; `tox.ini:39-43` sets `PYTHONPATH = {env:PATH}/testapp` for the `mypy` environment.
- `testapp/payments` is a symlink (`git ls-files -s` → mode `120000`) to the library, and the demo app's inner app is literally named `testmain`; `testapp/testapp/settings.py:10` contains *"Quick-start development settings - unsuitable for production"*.
- `docs/conf.py` is a Sphinx configuration file (`# Configuration file for the Sphinx documentation builder.`), not library code.

Expected counts for this run, using the same graph:

| | significant | represented | uncovered |
|---|---:|---:|---:|
| production modules | 27 | 16 | 11 |

Resulting production coverage: **16/27 = 59.3%** (the report says 24/55 = 43.6%).

Even if `docs/conf.py` is kept in the production set, the denominator is 28 and the ratio 57.1%; either way, 55 is not a production-source count. The qualification message should therefore name 11 production files, not 31 paths.

## 5. Actual behavior

Observed on the run above:

```text
Material source coverage gate: 24/55 significant source files represented (43.6%); repository-wide absence conclusions are prohibited.

Repository-wide absence conclusions are prohibited: 31 significant production source files are not represented by normalized paths.
```

The audit record (trimmed):

```json
{
  "event_type": "REPOSITORY_CONCLUSION_GATE",
  "decision": "PROHIBITED",
  "reason": "Repository-wide absence conclusions are prohibited: 31 significant production source files are not represented by normalized paths.",
  "rule_ids": ["REQUEST_COMPLETENESS_AND_MATERIAL_SOURCE_COVERAGE"],
  "subjects": ["docs/conf.py", "payments/coinbase/test_coinbase.py", "payments/core.py", "... 28 more"],
  "details": {
    "request_complete": true,
    "significant_source_file_count": 55,
    "represented_significant_source_file_count": 24,
    "significant_source_coverage_ratio": 0.4364,
    "significant_uncovered_files": ["... 31 paths ..."],
    "repository_wide_conclusions_allowed": false
  }
}
```

Composition of the 55 "significant production source files", computed by calling the shipped classifier on the run's own graph:

| bucket | significant | represented | uncovered |
|---|---:|---:|---:|
| `payments/**/test_*.py` (pytest) | 14 | 8 | 6 |
| `test_settings.py` (Django test settings) | 1 | 0 | 1 |
| `testapp/**` (demo Django project) | 12 | 0 | 12 |
| `docs/conf.py` (Sphinx) | 1 | 0 | 1 |
| production library modules | 27 | 16 | 11 |
| **total** | **55** | **24** | **31** |

So 20 of the 31 paths named as unrepresented *production* source are test, demo, or docs files, and the 43.6% figure understates production coverage by 15.6 percentage points. The six pytest modules counted as uncovered are `payments/coinbase/test_coinbase.py`, `payments/sagepay/test_sagepay.py`, `payments/sofort/test_sofort.py`, `payments/stripe/test_stripev3.py`, `payments/test_core.py`, and `payments/test_fields.py`.

On this particular repository the final gate decision is still defensible, because 11 real production modules (including `payments/core.py`, `payments/forms.py`, `payments/signals.py`, `payments/utils.py`, and `payments/widgets.py`) are genuinely unrepresented. The defect is that the reported quantity, the named files, and the reason given are wrong — and that on a repository with complete production coverage the same input set flips the decision (§6.3).

## 6. Evidence

### 6.1 Source

All paths are inside the installed wheel, `site-packages/shipreadyv2/`:

- `engine_sources/04_shipreadyv2_business_path_compiler.py:3056-3077` — `significant_production_source_files()`
  - `3062-3066`: the exclusion list is `"/test/", "/tests/", "_test.", ".test.", ".spec.", "/fixtures/", "/examples/", "/demo/", "/samples/", "/generated/", "/vendor/", "node_modules/", "next-env.d.ts"`.
  - `3069`: `lowered = f"/{file_path.casefold()}"`.
  - `3072-3073`: `if text_has_any(lowered, excluded_terms) or lowered.endswith(".d.ts"):` → `continue`.
  - `3074`: `meaningful_structure = bool(node.get("entities") or node.get("imports") or node.get("imported_by") or node.get("role_hints"))`.

  For `payments/paypal/test_paypal.py` the search string becomes `/payments/paypal/test_paypal.py`. It contains no `/test/`, no `/tests/`, and no `_test.` (the basename starts with `test_`, and the preceding character is `/`, not `_`), so the file passes the filter. `test_settings.py` → `/test_settings.py` passes for the same reason, and `testapp/manage.py` → `/testapp/manage.py` contains no `/demo/` or `/tests/`.

- `engine_sources/04_shipreadyv2_business_path_compiler.py:3080-3124` — `apply_repository_conclusion_gate()`
  - `3086`: denominator from the classifier; `3087`: represented set from `coverage["files_represented"]`.
  - `3089`: `ratio = len(significant_files & represented) / max(1, len(significant_files))`.
  - `3091`: `allowed = request_complete and not significant_uncovered`.
  - `3100`: the qualification message; `3102-3105`: the warning string; `3108-3115`: audit details and `subjects`.
- `engine_sources/05_shipreadyv2_critical_business_insight_selector_v4.py`
  - `1069-1071`: `repo_wide` drives `coverage_conf` (65 when false, 90 when true) and caps `candidate_conf`.
  - `1090`: `coverage_points = 2 if repo_wide else 1 if scan.completeness == "COMPLETE" else 0`.
  - `1180-1185`: `scan_qualification.material_source_coverage = "COMPLETE" if repo_wide else "PARTIAL_OR_UNKNOWN"`, plus `qualification_message`, serialised into each candidate.

### 6.2 Downstream effect in this run

The generated step-4 prompt (`<work dir>/b/run/shipreadyv2_step4_artifacts_v2_run_001/assembled_input.txt`) contains the qualification block six times — once for each of the six candidates included in that prompt (3 `SELECTED`, 3 `INVESTIGATION_GAP`) — e.g.:

```json
"scan_qualification": {
  "request_completeness": "COMPLETE",
  "material_source_coverage": "PARTIAL_OR_UNKNOWN",
  "repository_wide_conclusions_allowed": false,
  "qualification_message": "Repository-wide absence conclusions are prohibited: 31 significant production source files are not represented by normalized paths."
}
```

and each candidate carries `"coverage": 65` in `confidence` and `"coverage_reliability": 1` in `score`. The model is therefore told that material source coverage is partial and is given a list whose majority is test/demo code. Whether test paths should appear in normalized business paths at all is a separate question (#219, #238); this report is only about the production-source denominator.

The penalty is uniform across the run: all 30 candidate records (`3` selected, `16` rejected, `10` investigation gaps, `1` not selected by diversity) carry `coverage_reliability: 1` and `confidence.coverage: 65`. A corrected gate would add one point to every total, but it would not change the selection outcome here: the decision class is set by the proof obligations (`engine_sources/05_...:1056-1061`), and totals for non-eligible candidates are clamped to `MINIMUM_SELECTION_SCORE - 1 = 13` (`engine_sources/05_...:1092-1093`). The observable damage in this run is therefore the misreported coverage figures, the wrong uncovered-file list, and the `PARTIAL_OR_UNKNOWN` qualification sent to the model — not a different set of findings.

### 6.3 Self-contained reproduction — no analysis run or credits required

This is the smallest complete demonstration of the defect. It needs only `pip install unvibecode==0.3.15`; it does not use a run graph, model output, or hosted credits. The classifier admits all four test/demo conventions, then the gate reports **2/5 (40%)** even though **2/2 (100%)** of the production files are represented.

```python
import importlib.util, json, sys
from pathlib import Path
import shipreadyv2

engine = next((Path(shipreadyv2.__file__).parent / "engine_sources").glob("04_*.py"))
spec = importlib.util.spec_from_file_location("bpc", engine)
mod = importlib.util.module_from_spec(spec)
sys.modules["bpc"] = mod          # required: the module uses @dataclass
spec.loader.exec_module(mod)

node = {"entities": [{"name": "f"}], "imports": [], "imported_by": []}
graph_nodes = {p: dict(node) for p in [
    "service/handlers.py", "service/models.py",          # both represented
    "tests/test_handlers.py", "test_settings.py",
    "testapp/manage.py", "conftest.py",
]}
coverage = {"files_represented": ["service/handlers.py", "service/models.py"],
            "coverage_warnings": []}
scan = {"completeness": "COMPLETE", "expected_request_ids": ["r1"],
        "completed_request_ids": ["r1"]}
class Audit:
    def add(self, *a, **k): pass
details = mod.apply_repository_conclusion_gate(scan, coverage, graph_nodes, Audit())
print("production files represented: 2/2 (100%)")
print("significant_source_file_count:", details["significant_source_file_count"])
print("represented_significant_source_file_count:", details["represented_significant_source_file_count"])
print("significant_source_coverage_ratio:", details["significant_source_coverage_ratio"])
print("significant_uncovered_files:", details["significant_uncovered_files"])
print("repository_wide_conclusions_allowed:", details["repository_wide_conclusions_allowed"])
print("qualification_message:", scan["qualification_message"])
print("coverage_warnings:", coverage["coverage_warnings"])
```

Output:

```text
production files represented: 2/2 (100%)
significant_source_file_count: 5
represented_significant_source_file_count: 2
significant_source_coverage_ratio: 0.4
significant_uncovered_files: ['conftest.py', 'test_settings.py', 'testapp/manage.py']
repository_wide_conclusions_allowed: False
qualification_message: Repository-wide absence conclusions are prohibited: 3 significant production source files are not represented by normalized paths.
coverage_warnings: ['Material source coverage gate: 2/5 significant source files represented (40.0%); repository-wide absence conclusions are prohibited.']
```

`tests/test_handlers.py` is correctly filtered (it matches `/tests/`); the three files that defeat the filter are the other Python test/demo conventions. A repository with 100% production coverage can therefore be told that its absence conclusions are prohibited because its test settings and demo app are unrepresented.

### 6.4 Run-specific verification against the shipped code

Using the same import/bootstrap block as §6.3, load the run's graph and report:

```python
run = Path(r"<work dir>\b\run")   # from technical-logs/recovery-location.txt
graph = json.loads((run / "shipreadyv2_resolved_graph.json").read_text(encoding="utf-8"))
report = json.loads((run / "shipreadyv2_customer_business_flaw_report_v2_run_001.json").read_text(encoding="utf-8"))
nodes = {n["file"]: n for n in graph["nodes"]}
represented = set(report["coverage"]["coverage"]["files_represented"])

sig = mod.significant_production_source_files(nodes)
print(len(sig), len(sig & represented), len(sig - represented))
# 55 24 31

tests = {f for f in sig if f.rsplit("/", 1)[-1].startswith("test_")
         or f == "test_settings.py" or f.startswith("testapp/")}
prod = sig - tests - {"docs/conf.py"}
print(len(prod), len(prod & represented), len(prod - represented))
# 27 16 11
```

Observed output of this script against the run: `55 24 31` followed by `27 16 11`. The graph contains 66 nodes; the classifier is not randomised and does not depend on model output.

### 6.5 Sanitisation

No credentials, tokens, customer data, or private repository content are included. All paths and excerpts come from the public repository at the pinned commit and from local run artifacts.

## 7. Impact and scope

**Who is affected:** any Python repository that colocates tests with the package using `test_*.py` (the pytest default), or that keeps a `testapp/`-style demo project, `test_settings.py`, or a root `conftest.py` reachable by the graph. That layout is common for Django libraries and is exactly what this repository declares in `pyproject.toml`. Repositories that keep tests in a top-level `tests/` directory (for example Flask, used in #50) are unaffected, which is why the gap is layout-dependent and easy to miss.

**What is wrong:** a wrong answer, not a crash. The ratio, the qualification message, the audit subjects, and the material-coverage label handed to the model are all incorrect. In this run the reported production coverage is 43.6% instead of 59.3% — a 15.6-point understatement — and 20 of the 31 files named as unrepresented production source are tests, demo code, or docs.

**Worst case:** on a repository whose production files are all represented, the gate prohibits repository-wide conclusions solely because test/demo files are not (reproduced in §6.3), which changes the report's qualification, the coverage component of every candidate's score, and the `material_source_coverage` field sent to the model. The gate is the product's guardrail against unsupported absence claims; when its denominator is wrong in this direction it blocks valid conclusions rather than unsupported ones.

**Frequency:** deterministic. The classifier is a pure function of the resolved graph; the same graph reproduces 55/24/31 and 27/16/11 on every invocation. Observed in 1 of 1 completed business analyses; the second end-to-end attempt was blocked by exhausted hosted-service credits, not by nondeterminism.

## 8. Suspected cause / suggested fix (if known)

**Cause.** `significant_production_source_files()` uses a substring denylist built for path-segment layouts (`/test/`, `/tests/`) and suffix-like conventions (`_test.`, `.test.`, `.spec.`). pytest names test modules with a *prefix* (`test_*.py`), and the repository-specific files `test_settings.py`, `conftest.py`, and `testapp/` match no term. Because `lowered` is prefixed with `/` (`3069`), a leading `test_` in a basename can never be captured by `_test.`; the only reason `tests/test_x.py` works is the `/tests/` segment. `meaningful_structure` (`3074`) then admits the files because test modules import the library and define functions.

**Suggested fix.** Classify on the basename and on explicit test/demo conventions rather than only path substrings, for example:

- basename starts with `test_`, or equals `test_settings.py` or `conftest.py`;
- any path segment equals `testapp` or `testapps` (and similar demo-project conventions);
- keep the existing segment/suffix terms for JS/TS/Ruby.

Do not key this off pytest's `testpaths` setting: in this repository `testpaths = "payments"` names the whole library package, so treating it as a test root would exclude the production code as well.

The cleanest implementation is one shared `is_test_or_demo_path()` helper used by `significant_production_source_files()` (`04_...:3056`), `derive_reachability()` (`04_...:1562`), and `STRUCTURAL_EXCLUDED_PATH_PARTS` (`06_...:398-402`), so the three filters cannot drift apart again. Whether `docs/conf.py` should count as production is a separate judgement call; if docs configs stay in, the ratio is still 57.1%, not 43.6%.

**Validation.** Add a unit test that calls `apply_repository_conclusion_gate()` with two represented production modules plus `tests/test_handlers.py`, `test_settings.py`, `testapp/manage.py`, and `conftest.py`, and asserts `significant_source_file_count == 2`, `significant_uncovered_files == []`, and `repository_wide_conclusions_allowed is True`. That test currently fails with `5 / 3 uncovered / False`, as shown in §6.3.

**Blast radius of the fix.** Only the input set changes; the decision rule (`allowed = request_complete and not significant_uncovered`) and the ratio formula stay as they are.

## 9. Duplicate check

Searched open and closed issues in `FinanceFlash/unvibecode` on 31 October 2026 for: `significant production source files`, `significant source files`, `material source coverage`, `coverage gate`, `significant_source_file_count`, `significant_uncovered_files`, `43.6`, `PARTIAL_OR_UNKNOWN`, `coverage_reliability`, `denominator`, `excluded_terms`, `test_*.py`, `testapp`, `test settings`, `conftest`, `pytest`, `coverage`.

I also reviewed the 40 most recent Cohort 3 submissions (issues #306–#345) and all 33 results for `coverage`. None report this denominator; the closest Cohort 3 entries are #340 (chunker output validity), #342 (function-local import edges), #344–#345 (credential redaction), and #338 (UX), all of which concern different subsystems.

Closest existing issues and why this is distinct:

- **#241 — Structural Review flags Ruby RSpec test files (`spec/`, `*_spec.rb`) as production complexity hotspots.** The closest in category: the same idea that a test-file filter is incomplete. It concerns a different function (`STRUCTURAL_EXCLUDED_PATH_PARTS` in `06_...step4_v2_with_v4_inputs.py`, used by `structural_review_candidates`), a different output (a hotspot card in Risk Findings), and different conventions (Ruby `spec/`, `*_spec.rb`). Applying #241's suggested fix leaves `04_...business_path_compiler.py:3062-3066` untouched, so the denominator, the ratio, and the qualification message remain wrong; fixing #241 does not change this behaviour.
- **#50 — publishes a repository-wide "0 flaws" headline when the gate prohibits conclusions.** #50 quotes the gate's warning but takes the counts as given (`14/25`, `56.0%`) and is about *enforcing* the gate at the report and terminal boundaries. This report is about the gate *mis-counting its own inputs*. On #50's repository (Flask) tests live under `tests/`, which the current list already excludes, so the misclassification would not have appeared there; the two fixes are independent.
- **#219 — Test suite files assigned E1 direct evidence for core workflows**, and **#238 — Reachability canonicalization marks production workflows as TEST_DEMO_SAMPLE at HIGH confidence as soon as any test file is cited.** Both are about how test files are treated once they enter normalized paths / reachability labels. This report is about test files inflating the *production* denominator before reachability matters; it would remain after either fix.
- **#207 — Distinguish example-application workflows from core repository workflows**, and **#201 — Business workflow analysis fragments Flask request lifecycle…** Both concern example/test workflows being presented as core business workflows. This report concerns the coverage gate's file accounting and its qualification message, not the workflow map.
- **#258 — unique_symbol_via_resolved_module fallback resolves production imports to pytest fixtures in test files.** Same subsystem family (test-file awareness) but a different function (`_resolve_symbol`) and a different output (false `imports_symbol` edges in the Connected Code Map).
- **#331 — Connected Code Map: relative `.globals` import resolves `app_ctx` to `tests/conftest.py`.** Matching the word `conftest` only. It is about symbol-edge resolution choosing a test file as an import target, not about the production-source denominator. A fix there would not change `significant_production_source_files()`.
- **#148 — Warn when built-in directory filters hide supported source files.** Concerns directory-name exclusions (`env`, `.env`) hiding source, i.e. files missing from the scan, not files over-counted as production.

Searches for `significant_source_file_count`, `significant_uncovered_files`, `PARTIAL_OR_UNKNOWN`, `coverage_reliability`, `denominator`, `excluded_terms`, and `testapp` returned zero results; `test_*.py` returned only #201, discussed above; `conftest` returned only #258, also above; `material source coverage` and `coverage gate` returned only #50. If a maintainer considers a shared test-path predicate to be the right umbrella for #241 and this report, I am happy to have this closed in favour of that broader fix — but as filed, the affected function, artifact, and downstream consumer are different.
