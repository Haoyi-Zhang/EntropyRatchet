"""Regression tests for the frozen bibliography/citation integrity audit."""
from __future__ import annotations

import csv
import shutil
import tempfile
from pathlib import Path
import unittest

from audit_sources import run_audit


ROOT = Path(__file__).resolve().parents[1]


class SourceAuditTests(unittest.TestCase):
    def _copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        base = Path(tmp.name) / "artifact"
        shutil.copytree(ROOT, base, ignore=shutil.ignore_patterns("results", "__pycache__"))
        return tmp, base

    def test_current_source_packet_passes(self):
        result = run_audit(ROOT)
        self.assertTrue(result["passed"], result.get("errors"))
        self.assertGreaterEqual(result["reference_count"], 55)
        self.assertEqual(result["reference_count"], result["cited_reference_count"])
        self.assertFalse(result["network_resolution_performed"])

    def test_optional_manuscript_and_bbl_checks(self):
        tmp, base = self._copy()
        try:
            keys = (base / "inputs/manuscript-citations.txt").read_text().splitlines()
            manuscript = Path(tmp.name) / "main.tex"
            bbl = Path(tmp.name) / "main.bbl"
            manuscript.write_text("\\cite{" + ",".join(keys) + "}\n")
            bbl.write_text("\n".join(f"\\bibitem{{{key}}}" for key in keys) + "\n")
            result = run_audit(base, manuscript=manuscript, bbl=bbl)
            self.assertTrue(result["passed"], result.get("errors"))
            self.assertTrue(result["manuscript_source_compared"])
            self.assertTrue(result["printed_bbl_compared"])
            self.assertEqual(result["manuscript_citation_count"], len(keys))
            self.assertEqual(result["printed_bibliography_count"], len(keys))
        finally:
            tmp.cleanup()

    def test_optional_manuscript_drift_rejected(self):
        tmp, base = self._copy()
        try:
            keys = (base / "inputs/manuscript-citations.txt").read_text().splitlines()
            manuscript = Path(tmp.name) / "main.tex"
            manuscript.write_text("\\cite{" + ",".join(keys[1:]) + "}\n")
            self.assertFalse(run_audit(base, manuscript=manuscript)["passed"])
        finally:
            tmp.cleanup()

    def test_duplicate_bibtex_key_rejected(self):
        tmp, base = self._copy()
        try:
            path = base / "inputs/references.bib"
            text = path.read_text()
            first = text[: text.find("\n\n", text.find("@")) + 2]
            path.write_text(text + "\n" + first)
            self.assertFalse(run_audit(base)["passed"])
        finally:
            tmp.cleanup()

    def test_year_mismatch_rejected(self):
        tmp, base = self._copy()
        try:
            path = base / "inputs/bibliography_registry.csv"
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            rows[0]["year"] = "1900"
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader(); writer.writerows(rows)
            self.assertFalse(run_audit(base)["passed"])
        finally:
            tmp.cleanup()

    def test_uncited_reference_rejected(self):
        tmp, base = self._copy()
        try:
            path = base / "inputs/manuscript-citations.txt"
            lines = path.read_text().splitlines()
            path.write_text("\n".join(lines[1:]) + "\n")
            self.assertFalse(run_audit(base)["passed"])
        finally:
            tmp.cleanup()

    def test_generic_dblp_search_rejected(self):
        tmp, base = self._copy()
        try:
            for relative, locator_field in (("literature_matrix.csv", "stable_locator"),
                                             ("inputs/bibliography_registry.csv", "primary_locator")):
                path = base / relative
                with path.open(newline="") as handle:
                    rows = list(csv.DictReader(handle))
                rows[0][locator_field] = "https://dblp.org/search?q=not-a-record"
                if "locator_kind" in rows[0]: rows[0]["locator_kind"] = "dblp-record"
                with path.open("w", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                    writer.writeheader(); writer.writerows(rows)
            self.assertFalse(run_audit(base)["passed"])
        finally:
            tmp.cleanup()


    def test_non_doi_bibtex_url_mismatch_rejected(self):
        tmp, base = self._copy()
        try:
            registry_path = base / "inputs/bibliography_registry.csv"
            with registry_path.open(newline="") as handle:
                target = next(row for row in csv.DictReader(handle) if row["locator_kind"] != "doi")
            path = base / "inputs/references.bib"
            text = path.read_text()
            text = text.replace(
                "url={" + target["primary_locator"] + "}",
                "url={https://example.invalid/wrong-record}",
                1,
            )
            path.write_text(text)
            self.assertFalse(run_audit(base)["passed"])
        finally:
            tmp.cleanup()

    def test_inproceedings_missing_pages_rejected(self):
        tmp, base = self._copy()
        try:
            path = base / "inputs/references.bib"
            text = path.read_text()
            text = text.replace("  pages={195--211},\n", "", 1)
            path.write_text(text)
            self.assertFalse(run_audit(base)["passed"])
        finally:
            tmp.cleanup()

    def test_duplicate_primary_locator_rejected(self):
        tmp, base = self._copy()
        try:
            matrix_path = base / "literature_matrix.csv"
            registry_path = base / "inputs/bibliography_registry.csv"
            with matrix_path.open(newline="") as handle:
                matrix_rows = list(csv.DictReader(handle))
                matrix_fields = list(matrix_rows[0].keys())
            with registry_path.open(newline="") as handle:
                registry_rows = list(csv.DictReader(handle))
                registry_fields = list(registry_rows[0].keys())
            duplicate = matrix_rows[0]["stable_locator"]
            matrix_rows[1]["stable_locator"] = duplicate
            registry_rows[1]["primary_locator"] = duplicate
            registry_rows[1]["locator_kind"] = registry_rows[0]["locator_kind"]
            with matrix_path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=matrix_fields)
                writer.writeheader(); writer.writerows(matrix_rows)
            with registry_path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=registry_fields)
                writer.writeheader(); writer.writerows(registry_rows)
            self.assertFalse(run_audit(base)["passed"])
        finally:
            tmp.cleanup()

    def test_missing_external_locator_rejected(self):
        tmp, base = self._copy()
        try:
            path = base / "external_resources.csv"
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            with (base / "literature_matrix.csv").open(newline="") as handle:
                target = next(csv.DictReader(handle))["stable_locator"]
            for row in rows:
                if row["scholarly_or_official_url"] == target:
                    row["scholarly_or_official_url"] = "https://example.invalid/missing"
                    break
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader(); writer.writerows(rows)
            self.assertFalse(run_audit(base)["passed"])
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
