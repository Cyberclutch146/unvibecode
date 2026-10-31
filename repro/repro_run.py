"""Run-specific verification against the shipped classifier.

Requires:
  * the shipped wheel (pip install unvibecode==0.3.15)
  * the retained analysis run directory, passed as an argument or via UNVIBE_RUN

Usage:

    python repro_run.py "C:\\path\\to\\uvc-xxxx\\b\\run"
    # or
    set UNVIBE_RUN=C:\\path\\to\\uvc-xxxx\\b\\run
    python repro_run.py

The run directory is printed by UnvibeCode in
`technical-logs/recovery-location.txt` and contains:

    shipreadyv2_resolved_graph.json
    shipreadyv2_customer_business_flaw_report_v2_run_001.json

Expected output (django-payments @ 5607e9e, run target-unvibecode-analysis-20261026_150012):

    55 24 31
    27 16 11
"""

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import shipreadyv2


def load_compiler():
    engine = next((Path(shipreadyv2.__file__).parent / "engine_sources").glob("04_*.py"))
    spec = importlib.util.spec_from_file_location("bpc", engine)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bpc"] = mod
    spec.loader.exec_module(mod)
    return mod, engine


def resolve_run_dir(cli_value: str | None) -> Path:
    raw = cli_value or os.environ.get("UNVIBE_RUN")
    if not raw:
        raise SystemExit(
            "Pass the run directory as an argument or set UNVIBE_RUN.\n"
            "Find it in <results>/technical-logs/recovery-location.txt"
        )
    run = Path(raw).expanduser()
    if not run.is_dir():
        raise SystemExit(f"Run directory not found: {run}")
    return run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", nargs="?", help="Path to the analysis <work dir>/b/run folder")
    args = parser.parse_args()

    run = resolve_run_dir(args.run_dir)
    graph_path = run / "shipreadyv2_resolved_graph.json"
    report_path = run / "shipreadyv2_customer_business_flaw_report_v2_run_001.json"
    for path in (graph_path, report_path):
        if not path.is_file():
            raise SystemExit(f"Missing required artifact: {path}")

    mod, engine = load_compiler()
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))

    nodes = {n["file"]: n for n in graph["nodes"]}
    represented = set(report["coverage"]["coverage"]["files_represented"])

    sig = mod.significant_production_source_files(nodes)
    sig_counts = (len(sig), len(sig & represented), len(sig - represented))
    print(*sig_counts)  # 55 24 31

    tests = {
        f
        for f in sig
        if f.rsplit("/", 1)[-1].startswith("test_")
        or f == "test_settings.py"
        or f.startswith("testapp/")
    }
    prod = sig - tests - {"docs/conf.py"}
    prod_counts = (len(prod), len(prod & represented), len(prod - represented))
    print(*prod_counts)  # 27 16 11

    print()
    print("engine:", engine)
    print("engine sha256:", hashlib_sha256(engine))
    print("graph nodes:", len(nodes))

    passed = sig_counts == (55, 24, 31) and prod_counts == (27, 16, 11)
    print("COUNTS MATCH" if passed else "UNEXPECTED COUNTS — engine or run changed")
    return 0 if passed else 1


def hashlib_sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
