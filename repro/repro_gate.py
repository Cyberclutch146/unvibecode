"""Self-contained reproduction of the coverage-gate denominator bug.

Requires only the shipped wheel:

    pip install unvibecode==0.3.15
    python repro_gate.py

No analysis run, graph, model output, or hosted credits are needed.

Expected output:

    production files represented: 2/2 (100%)
    significant_source_file_count: 5
    represented_significant_source_file_count: 2
    significant_source_coverage_ratio: 0.4
    significant_uncovered_files: ['conftest.py', 'test_settings.py', 'testapp/manage.py']
    repository_wide_conclusions_allowed: False
    qualification_message: Repository-wide absence conclusions are prohibited: 3 significant production source files are not represented by normalized paths.
    coverage_warnings: ['Material source coverage gate: 2/5 significant source files represented (40.0%); repository-wide absence conclusions are prohibited.']
"""

import importlib.util
import sys
from pathlib import Path

import shipreadyv2


def load_compiler():
    engine = next((Path(shipreadyv2.__file__).parent / "engine_sources").glob("04_*.py"))
    spec = importlib.util.spec_from_file_location("bpc", engine)
    mod = importlib.util.module_from_spec(spec)
    # Required: the engine module defines @dataclass types that resolve via sys.modules.
    sys.modules["bpc"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = load_compiler()

    node = {"entities": [{"name": "f"}], "imports": [], "imported_by": []}
    graph_nodes = {
        path: dict(node)
        for path in [
            "service/handlers.py",
            "service/models.py",          # both production files are represented
            "tests/test_handlers.py",     # correctly filtered (/tests/)
            "test_settings.py",           # admitted as production
            "testapp/manage.py",          # admitted as production
            "conftest.py",                # admitted as production
        ]
    }
    coverage = {
        "files_represented": ["service/handlers.py", "service/models.py"],
        "coverage_warnings": [],
    }
    scan = {
        "completeness": "COMPLETE",
        "expected_request_ids": ["r1"],
        "completed_request_ids": ["r1"],
    }

    class Audit:
        def add(self, *args, **kwargs):
            pass

    details = mod.apply_repository_conclusion_gate(scan, coverage, graph_nodes, Audit())

    print("production files represented: 2/2 (100%)")
    print("significant_source_file_count:", details["significant_source_file_count"])
    print(
        "represented_significant_source_file_count:",
        details["represented_significant_source_file_count"],
    )
    print("significant_source_coverage_ratio:", details["significant_source_coverage_ratio"])
    print("significant_uncovered_files:", details["significant_uncovered_files"])
    print(
        "repository_wide_conclusions_allowed:",
        details["repository_wide_conclusions_allowed"],
    )
    print("qualification_message:", scan["qualification_message"])
    print("coverage_warnings:", coverage["coverage_warnings"])

    passed = (
        details["significant_source_file_count"] == 5
        and details["represented_significant_source_file_count"] == 2
        and details["significant_source_coverage_ratio"] == 0.4
        and details["repository_wide_conclusions_allowed"] is False
    )
    print()
    print("BUG REPRODUCED" if passed else "UNEXPECTED OUTPUT — bug may be fixed or engine changed")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
