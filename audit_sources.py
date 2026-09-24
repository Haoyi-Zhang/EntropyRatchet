#!/usr/bin/env python3
"""Offline bibliography/citation integrity audit.

The checker proves internal agreement among the frozen BibTeX snapshot, citation
key snapshot, literature matrix, bibliography registry, and external-resource
ledger.  It intentionally does not claim that syntax validation resolves a URL,
reads a paper, or independently establishes a cited theorem.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

MINIMUM_REFERENCES = 55
REQUIRED_REGISTRY_FIELDS = (
    "bib_key", "title", "authors", "year", "entry_type", "primary_locator",
    "locator_kind", "verification_status", "verification_basis", "access_date",
)
PUBLICATION_REQUIRED_FIELDS = {
    "article": ("journal", "volume", "pages"),
    "book": ("publisher",),
    "inproceedings": ("booktitle", "pages"),
    "phdthesis": ("school",),
}


class AuditFailure(ValueError):
    """Raised for malformed frozen source evidence."""


def _balanced_entries(text: str) -> List[Tuple[str, str, str]]:
    entries: List[Tuple[str, str, str]] = []
    pos = 0
    start_re = re.compile(r"@([A-Za-z]+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
    while True:
        match = start_re.search(text, pos)
        if not match:
            break
        depth = 1
        i = match.end()
        while i < len(text) and depth:
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
        if depth:
            raise AuditFailure(f"unterminated BibTeX entry {match.group(2)!r}")
        entries.append((match.group(1).lower(), match.group(2), text[match.end(): i - 1]))
        pos = i
    if not entries:
        raise AuditFailure("no BibTeX entries found")
    return entries


def _split_fields(body: str) -> List[str]:
    chunks: List[str] = []
    start = 0
    depth = 0
    quoted = False
    escaped = False
    for i, ch in enumerate(body):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"' and depth == 0:
            quoted = not quoted
        elif not quoted:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    raise AuditFailure("unbalanced field braces")
            elif ch == "," and depth == 0:
                chunks.append(body[start:i])
                start = i + 1
    if body[start:].strip():
        chunks.append(body[start:])
    return chunks


def _strip_value(value: str) -> str:
    value = value.strip()
    while len(value) >= 2 and ((value[0] == "{" and value[-1] == "}") or
                               (value[0] == '"' and value[-1] == '"')):
        value = value[1:-1].strip()
    return value


def parse_bibtex(path: Path) -> Tuple[Dict[str, Dict[str, str]], List[str]]:
    text = path.read_text(encoding="utf-8")
    parsed: Dict[str, Dict[str, str]] = {}
    order: List[str] = []
    for entry_type, key, body in _balanced_entries(text):
        if key in parsed:
            raise AuditFailure(f"duplicate BibTeX key: {key}")
        fields: Dict[str, str] = {"entry_type": entry_type}
        for chunk in _split_fields(body):
            if not chunk.strip():
                continue
            if "=" not in chunk:
                raise AuditFailure(f"malformed field in {key}: {chunk.strip()!r}")
            name, value = chunk.split("=", 1)
            name = name.strip().lower()
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name):
                raise AuditFailure(f"invalid field name in {key}: {name!r}")
            if name in fields:
                raise AuditFailure(f"duplicate field {name!r} in {key}")
            fields[name] = _strip_value(value)
        for required in ("title", "author", "year"):
            if not fields.get(required):
                raise AuditFailure(f"BibTeX entry {key} lacks {required}")
        parsed[key] = fields
        order.append(key)
    return parsed, order


_ACCENTS = {
    "\\'e": "é", "\\'o": "ó", '\\"e': "ë", '\\"o': "ö", '\\"u': "ü",
    "\\`i": "ì", "\\cC": "Ç", "\\c{C}": "Ç",
}


def text_norm(value: str) -> str:
    value = value.replace("---", "-").replace("--", "-")
    for source, target in _ACCENTS.items():
        value = value.replace("{" + source + "}", target).replace(source + "}", target).replace(source, target)
    value = re.sub(r"\\[A-Za-z]+\s*", "", value)
    value = value.replace("{", "").replace("}", "")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def read_csv(path: Path, required: Sequence[str]) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AuditFailure(f"missing CSV header: {path}")
        missing = [field for field in required if field not in reader.fieldnames]
        if missing:
            raise AuditFailure(f"{path} lacks columns: {', '.join(missing)}")
        return [dict(row) for row in reader]


def rows_by_key(rows: Iterable[Mapping[str, str]], source: str) -> Dict[str, Mapping[str, str]]:
    output: Dict[str, Mapping[str, str]] = {}
    for row in rows:
        key = row.get("bib_key", "").strip()
        if not key:
            raise AuditFailure(f"empty bib_key in {source}")
        if key in output:
            raise AuditFailure(f"duplicate bib_key {key!r} in {source}")
        output[key] = row
    return output


def locator_kind(locator: str) -> str:
    locator = locator.strip()
    if re.fullmatch(r"https://doi\.org/10\.\d{4,9}/\S+", locator, re.IGNORECASE):
        return "doi"
    if re.fullmatch(r"https://arxiv\.org/abs/[A-Za-z0-9.\-/]+", locator):
        return "arxiv"
    if re.fullmatch(r"https://eprint\.iacr\.org/\d{4}/\d+", locator):
        return "eprint"
    if re.fullmatch(r"https://dblp\.org/rec/[A-Za-z0-9_.\-/]+(?:\.html)?", locator):
        return "dblp-record"
    if re.fullmatch(r"https://(?:crypto\.ethz\.ch|authors\.library\.caltech\.edu)/\S+", locator):
        return "institutional-or-scholarly-record"
    raise AuditFailure(f"unsupported or non-persistent locator form: {locator!r}")



def extract_manuscript_citations(path: Path) -> set[str]:
    """Extract citation keys from a LaTeX manuscript after removing comments."""
    text = path.read_text(encoding="utf-8")
    uncommented = "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())
    keys: set[str] = set()
    pattern = re.compile(
        r"\\cite[A-Za-z]*\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}",
        re.MULTILINE,
    )
    for match in pattern.finditer(uncommented):
        keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    if not keys:
        raise AuditFailure(f"no citation keys found in manuscript: {path}")
    return keys


def extract_bbl_keys(path: Path) -> set[str]:
    """Extract printed bibliography keys from a BibTeX-generated .bbl file."""
    text = path.read_text(encoding="utf-8")
    keys = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", text))
    if not keys:
        raise AuditFailure(f"no bibliography items found in BBL: {path}")
    return keys


def _set_diff(label_a: str, a: set[str], label_b: str, b: set[str], errors: List[str]) -> None:
    missing = sorted(a - b)
    extra = sorted(b - a)
    if missing:
        errors.append(f"{label_b} misses keys present in {label_a}: {missing}")
    if extra:
        errors.append(f"{label_b} has keys absent from {label_a}: {extra}")


def run_audit(base: Path, manuscript: Path | None = None, bbl: Path | None = None) -> Dict[str, object]:
    inputs = base / "inputs"
    errors: List[str] = []
    warnings: List[str] = []
    try:
        bib, bib_order = parse_bibtex(inputs / "references.bib")
        citations = [line.strip() for line in (inputs / "manuscript-citations.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
        citation_counts = Counter(citations)
        if any(count != 1 for count in citation_counts.values()):
            duplicates = sorted(key for key, count in citation_counts.items() if count != 1)
            raise AuditFailure(f"duplicate citation keys in snapshot: {duplicates}")
        matrix_rows = read_csv(base / "literature_matrix.csv", ("bib_key", "title", "authors", "year", "entry_type", "stable_locator"))
        registry_rows = read_csv(inputs / "bibliography_registry.csv", REQUIRED_REGISTRY_FIELDS)
        external_rows = read_csv(base / "external_resources.csv", ("name", "scholarly_or_official_url", "access_date", "resource_type"))
        matrix = rows_by_key(matrix_rows, "literature_matrix.csv")
        registry = rows_by_key(registry_rows, "bibliography_registry.csv")
        bib_keys, citation_keys = set(bib), set(citations)
        matrix_keys, registry_keys = set(matrix), set(registry)
        _set_diff("BibTeX", bib_keys, "citation snapshot", citation_keys, errors)
        _set_diff("BibTeX", bib_keys, "literature matrix", matrix_keys, errors)
        _set_diff("BibTeX", bib_keys, "bibliography registry", registry_keys, errors)
        if len(bib) < MINIMUM_REFERENCES:
            errors.append(f"reference count {len(bib)} is below required minimum {MINIMUM_REFERENCES}")
        locators: List[str] = []
        for key in sorted(bib_keys & matrix_keys & registry_keys):
            entry, row, reg = bib[key], matrix[key], registry[key]
            comparisons = (
                ("title", entry["title"], row["title"]),
                ("author", entry["author"], row["authors"]),
                ("year", entry["year"], row["year"]),
                ("entry_type", entry["entry_type"], row["entry_type"]),
                ("registry title", row["title"], reg["title"]),
                ("registry authors", row["authors"], reg["authors"]),
                ("registry year", row["year"], reg["year"]),
                ("registry type", row["entry_type"], reg["entry_type"]),
            )
            for label, left, right in comparisons:
                if text_norm(left) != text_norm(right):
                    errors.append(f"{key}: {label} mismatch: {left!r} != {right!r}")
            locator = row["stable_locator"].strip()
            if locator != reg["primary_locator"].strip():
                errors.append(f"{key}: matrix and registry locator mismatch")
                continue
            try:
                actual_kind = locator_kind(locator)
            except AuditFailure as exc:
                errors.append(f"{key}: {exc}")
                continue
            if actual_kind != reg["locator_kind"].strip():
                errors.append(f"{key}: locator kind {actual_kind!r} != registry {reg['locator_kind']!r}")
            if "dblp.org/search" in locator:
                errors.append(f"{key}: generic DBLP search URL is not an acceptable record locator")
            required_fields = PUBLICATION_REQUIRED_FIELDS.get(entry["entry_type"], ())
            missing_fields = [field for field in required_fields if not entry.get(field, "").strip()]
            if missing_fields:
                errors.append(f"{key}: incomplete publication metadata; missing {missing_fields}")
            if actual_kind == "doi":
                expected_doi = locator.split("doi.org/", 1)[1]
                if entry.get("doi", "").casefold() != expected_doi.casefold():
                    errors.append(f"{key}: BibTeX DOI does not match primary locator")
            else:
                if entry.get("url", "").strip() != locator:
                    errors.append(f"{key}: BibTeX URL does not match non-DOI primary locator")
            locators.append(locator)
        manuscript_keys: set[str] | None = None
        printed_keys: set[str] | None = None
        if manuscript is not None:
            manuscript_keys = extract_manuscript_citations(manuscript)
            _set_diff("citation snapshot", citation_keys, "manuscript", manuscript_keys, errors)
        if bbl is not None:
            printed_keys = extract_bbl_keys(bbl)
            _set_diff("BibTeX", bib_keys, "printed BBL", printed_keys, errors)

        duplicated_locators = sorted(locator for locator, count in Counter(locators).items() if count > 1)
        if duplicated_locators:
            errors.append(f"duplicate primary locators: {duplicated_locators}")
        external_urls = {row["scholarly_or_official_url"].strip() for row in external_rows}
        missing_external = sorted(set(locators) - external_urls)
        if missing_external:
            errors.append(f"external_resources.csv misses primary locators: {missing_external}")
        statuses = Counter(row["verification_status"].strip() for row in registry_rows)
        if not statuses.get("publisher_archive_or_institutional_record_checked"):
            warnings.append("no registry entries are marked as publisher/archive/institutional-record checked")
        result: Dict[str, object] = {
            "schema": "source-audit-v2",
            "passed": not errors,
            "network_resolution_performed": False,
            "scope": "offline internal consistency and persistent-identifier-form audit; not independent content verification",
            "minimum_reference_count": MINIMUM_REFERENCES,
            "reference_count": len(bib),
            "cited_reference_count": len(citation_keys),
            "matrix_row_count": len(matrix_rows),
            "registry_row_count": len(registry_rows),
            "external_resource_row_count": len(external_rows),
            "publication_metadata_complete_count": sum(
                not any(not entry.get(field, "").strip()
                        for field in PUBLICATION_REQUIRED_FIELDS.get(entry["entry_type"], ()))
                for entry in bib.values()
            ),
            "bibtex_locator_count": sum(bool(entry.get("doi") or entry.get("url")) for entry in bib.values()),
            "locator_kind_counts": dict(sorted(Counter(locator_kind(x) for x in locators if x).items())) if not any("unsupported or non-persistent" in e for e in errors) else {},
            "verification_status_counts": dict(sorted(statuses.items())),
            "bib_order_is_unique": len(bib_order) == len(set(bib_order)),
            "manuscript_source_compared": manuscript is not None,
            "manuscript_citation_count": len(manuscript_keys) if manuscript_keys is not None else None,
            "printed_bbl_compared": bbl is not None,
            "printed_bibliography_count": len(printed_keys) if printed_keys is not None else None,
            "errors": errors,
            "warnings": warnings,
        }
        return result
    except (AuditFailure, OSError, UnicodeError, csv.Error) as exc:
        return {
            "schema": "source-audit-v2", "passed": False,
            "network_resolution_performed": False,
            "scope": "offline internal consistency and persistent-identifier-form audit; not independent content verification",
            "manuscript_source_compared": manuscript is not None,
            "printed_bbl_compared": bbl is not None,
            "errors": [str(exc)], "warnings": warnings,
        }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent,
                        help="artifact repository root (default: directory containing this script)")
    parser.add_argument("--output", type=Path, default=Path("results/source-audit.json"))
    parser.add_argument("--manuscript", type=Path,
                        help="optional LaTeX manuscript whose live citation keys must match the frozen snapshot")
    parser.add_argument("--bbl", type=Path,
                        help="optional generated BBL whose printed keys must match the frozen bibliography")
    args = parser.parse_args(argv)
    manuscript = args.manuscript.resolve() if args.manuscript else None
    bbl = args.bbl.resolve() if args.bbl else None
    result = run_audit(args.base.resolve(), manuscript=manuscript, bbl=bbl)
    output = args.output if args.output.is_absolute() else args.base.resolve() / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    sys.exit(main())
