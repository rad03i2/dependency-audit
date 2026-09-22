from __future__ import annotations

import argparse
import json
import sys

from .core import audit

LEVELS = {"info": 1, "warning": 2, "error": 3}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dependency-audit", description="Audit local dependency manifests without network access.")
    p.add_argument("path", nargs="?", default=".", help="Project directory (default: current directory)")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    p.add_argument("--fail-on", choices=("info", "warning", "error", "never"), default="error", help="Exit 1 at or above this severity")
    p.add_argument("--version", action="version", version="dependency-audit 1.0.0")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = audit(args.path)
    except (ValueError, OSError) as exc:
        print(f"dependency-audit: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"Dependency Audit — {report.root}")
        print(f"Manifests: {', '.join(report.manifests) or 'none'} | Dependencies: {report.dependencies}")
        if not report.findings:
            print("No manifest hygiene findings.")
        for f in report.findings:
            package = f" [{f.package}]" if f.package else ""
            where = f" ({f.file})" if f.file else ""
            print(f"{f.severity.upper():7} {f.code}{package}: {f.message}{where}")
        c = report.counts
        print(f"Summary: {c['error']} error(s), {c['warning']} warning(s), {c['info']} info")
    if args.fail_on == "never":
        return 0
    threshold = LEVELS[args.fail_on]
    return int(any(LEVELS[f.severity] >= threshold for f in report.findings))


if __name__ == "__main__":
    raise SystemExit(main())
