# Repro: coverage-gate denominator bug

Two scripts back the Track 1 issue
[`ISSUE_coverage_gate_test_files.md`](../ISSUE_coverage_gate_test_files.md).

| Script | Needs | Proves |
|---|---|---|
| `repro_gate.py` | only the wheel | The shipped gate turns **2/2 (100%) production coverage** into **2/5 (40%)** and blocks repository-wide conclusions. |
| `repro_run.py` | wheel + retained run artifacts | The same classifier produces the real run's **55 / 24 / 31** and the production-only **27 / 16 / 11**. |

Neither script uses the hosted analysis service, so no API credits are spent.

## Install

```powershell
python -m pip install "unvibecode==0.3.15"
```

Confirm the engine version:

```powershell
python -c "import shipreadyv2, pathlib; print(next((pathlib.Path(shipreadyv2.__file__).parent / 'engine_sources').glob('04_*.py')))"
```

The Windows wheels for 0.3.15 bundle
`04_shipreadyv2_business_path_compiler.py` with SHA-256
`b98412a824acd0872b05ea3b83d7b663f441db201c080b821dbd54917ef77387`.

## 1. Self-contained repro (recommended for reviewers)

```powershell
python repro_gate.py
```

Expected output:

```text
production files represented: 2/2 (100%)
significant_source_file_count: 5
represented_significant_source_file_count: 2
significant_source_coverage_ratio: 0.4
significant_uncovered_files: ['conftest.py', 'test_settings.py', 'testapp/manage.py']
repository_wide_conclusions_allowed: False
qualification_message: Repository-wide absence conclusions are prohibited: 3 significant production source files are not represented by normalized paths.
coverage_warnings: ['Material source coverage gate: 2/5 significant source files represented (40.0%); repository-wide absence conclusions are prohibited.']

BUG REPRODUCED
```

Why the three extras appear:

| File | Filter result | Reason |
|---|---|---|
| `tests/test_handlers.py` | excluded (correct) | matches `/tests/` |
| `test_settings.py` | **counted as production** | no term matches `test_` prefix |
| `testapp/manage.py` | **counted as production** | `testapp/` is not in the list |
| `conftest.py` | **counted as production** | not in the list |

## 2. Run-specific verification

The run directory is the `<work dir>/b/run` path printed in
`<results>/technical-logs/recovery-location.txt`.

```powershell
python repro_run.py "C:\Users\<you>\AppData\Local\Temp\uvc-xxxx\b\run"
# or
$env:UNVIBE_RUN = "C:\Users\<you>\AppData\Local\Temp\uvc-xxxx\b\run"
python repro_run.py
```

Expected output:

```text
55 24 31
27 16 11

engine: ...\shipreadyv2\engine_sources\04_shipreadyv2_business_path_compiler.py
engine sha256: b98412a824acd0872b05ea3b83d7b663f441db201c080b821dbd54917ef77387
graph nodes: 66
COUNTS MATCH
```

Reference run: `jazzband/django-payments` at
`5607e9e88762df9831980832c194f49b227dbe93`, analysis
`target-unvibecode-analysis-20261026_150012`, UnvibeCode 0.3.15,
Windows 11 (10.0.26200), Python 3.12.5.

## Notes

- Both scripts exit non-zero if the observed numbers differ from the documented
  ones, so a future engine change is obvious rather than silent.
- No credentials, customer data, or private repository content is required or
  printed.
