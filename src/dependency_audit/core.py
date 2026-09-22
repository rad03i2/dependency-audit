from __future__ import annotations

import json
import re
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REQ_NAME = re.compile(r"^\s*([A-Za-z0-9_.-]+)")
EXACT_PY = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*([^\s;]+)")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    package: str
    message: str
    file: str


@dataclass
class AuditReport:
    root: str
    manifests: list[str]
    dependencies: int
    findings: list[Finding]

    @property
    def counts(self) -> dict[str, int]:
        return {level: sum(f.severity == level for f in self.findings) for level in ("error", "warning", "info")}

    def to_dict(self) -> dict:
        data = asdict(self)
        data["counts"] = self.counts
        return data


def _python_entries(path: Path) -> Iterable[tuple[str, str]]:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(("-r", "--requirement", "-c", "--constraint", "--")):
            continue
        match = REQ_NAME.match(line)
        if match:
            yield match.group(1), line


def _pyproject_entries(path: Path) -> Iterable[tuple[str, str]]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    for item in project.get("dependencies", []) or []:
        match = REQ_NAME.match(item)
        if match:
            yield match.group(1), item
    for group in (project.get("optional-dependencies", {}) or {}).values():
        for item in group:
            match = REQ_NAME.match(item)
            if match:
                yield match.group(1), item


def _node_entries(path: Path) -> Iterable[tuple[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    for section in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        for name, spec in (data.get(section, {}) or {}).items():
            yield name, str(spec)


def _classify(name: str, spec: str, source: str) -> list[Finding]:
    findings: list[Finding] = []
    lowered = spec.lower().strip()
    if source.endswith("package.json"):
        if lowered in ("*", "latest", ""):
            findings.append(Finding("error", "UNBOUNDED", name, "Dependency is not version-bounded.", source))
        elif lowered.startswith(("git+", "git://", "http://", "https://", "file:", "github:")):
            findings.append(Finding("warning", "NON_REGISTRY", name, "Dependency uses a non-registry source; review reproducibility and trust.", source))
        elif lowered.startswith(("^", "~", ">", "<")):
            findings.append(Finding("info", "RANGE", name, "Dependency uses a version range; keep a lockfile for reproducible installs.", source))
    else:
        if "@" in spec and "http" in lowered:
            findings.append(Finding("warning", "DIRECT_URL", name, "Dependency is installed from a direct URL; review source trust.", source))
        elif EXACT_PY.match(spec):
            pass
        elif any(op in spec for op in (">", "<", "~=", "!=")):
            findings.append(Finding("info", "RANGE", name, "Dependency uses a version range; use a lock/constraints file when reproducibility matters.", source))
        else:
            findings.append(Finding("warning", "UNPINNED", name, "Dependency has no explicit version constraint.", source))
    return findings


def audit(root: str | Path = ".") -> AuditReport:
    base = Path(root).resolve()
    if not base.is_dir():
        raise ValueError(f"Not a directory: {base}")
    candidates = [base / "pyproject.toml", base / "requirements.txt", base / "package.json"]
    manifests: list[str] = []
    findings: list[Finding] = []
    total = 0
    seen: dict[str, tuple[str, str]] = {}
    for path in candidates:
        if not path.is_file():
            continue
        rel = path.name
        manifests.append(rel)
        try:
            if rel == "pyproject.toml":
                entries = list(_pyproject_entries(path))
            elif rel == "package.json":
                entries = list(_node_entries(path))
            else:
                entries = list(_python_entries(path))
        except (OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
            findings.append(Finding("error", "INVALID_MANIFEST", "", f"Could not parse manifest: {exc}", rel))
            continue
        total += len(entries)
        for name, spec in entries:
            key = name.casefold().replace("_", "-")
            if key in seen and seen[key][0] != spec:
                findings.append(Finding("warning", "CONFLICTING_SPEC", name, f"Different specifications found: {seen[key][0]!r} and {spec!r}.", rel))
            else:
                seen[key] = (spec, rel)
            findings.extend(_classify(name, spec, rel))
    if not manifests:
        findings.append(Finding("error", "NO_MANIFEST", "", "No supported dependency manifest found.", ""))
    if (base / "package.json").is_file() and not any((base / n).is_file() for n in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml")):
        findings.append(Finding("warning", "NO_LOCKFILE", "", "Node.js project has no recognized lockfile.", "package.json"))
    return AuditReport(str(base), manifests, total, findings)
