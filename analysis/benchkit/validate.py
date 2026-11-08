"""Schema + convention validation for raw result files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from jsonschema import Draft202012Validator

from . import SCHEMA_PATH
from .io import iter_jsonl_files

FILENAME_RE = re.compile(
    r"^(?P<date>\d{8})_(?P<platform>flutter|android_native|ios_native)_"
    r"(?P<model>[a-z0-9_]+?)_(?P<precision>fp32|fp16|int8)_"
    r"(?P<delegate>cpu|gpu|nnapi|coreml)_s(?P<session>\d{2})\.jsonl$"
)


@dataclass
class FileReport:
    path: Path
    n_records: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_validator(schema_path: Path = SCHEMA_PATH) -> Draft202012Validator:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def validate_file(path: Path, validator: Draft202012Validator, *, allow_synthetic: bool = False,
                  max_errors: int = 20) -> FileReport:
    """Validate one JSONL file: filename convention, JSON syntax, schema, consistency, synthetic flag."""
    report = FileReport(path=Path(path))
    m = FILENAME_RE.match(report.path.name)
    if not m:
        report.errors.append("filename does not match <YYYYMMDD>_<platform>_<model>_<precision>_<delegate>_sNN.jsonl")

    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if len(report.errors) >= max_errors:
                report.errors.append("... (truncated)")
                break
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                report.errors.append(f"line {lineno}: invalid JSON ({exc.msg})")
                continue
            report.n_records += 1
            for err in validator.iter_errors(rec):
                loc = "/".join(str(p) for p in err.absolute_path) or "<record>"
                report.errors.append(f"line {lineno}: {loc}: {err.message}")
            if rec.get("synthetic") and not allow_synthetic:
                report.errors.append(f"line {lineno}: synthetic record found outside test fixtures")
            if m:
                for key, group in (("platform", "platform"), ("precision", "precision"), ("delegate", "delegate")):
                    if rec.get(key) is not None and rec.get(key) != m.group(group):
                        report.errors.append(f"line {lineno}: {key}={rec.get(key)!r} disagrees with filename")
                if rec.get("session") is not None and rec.get("session") != int(m.group("session")):
                    report.errors.append(f"line {lineno}: session disagrees with filename")
    if report.n_records == 0 and not report.errors:
        report.errors.append("file has no records")
    return report


def validate_tree(root: Path, *, allow_synthetic: bool = False) -> list[FileReport]:
    validator = load_validator()
    return [validate_file(p, validator, allow_synthetic=allow_synthetic) for p in iter_jsonl_files(root)]
