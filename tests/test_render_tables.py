"""Regress the scientific event and deterministic result-to-table projection."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from render_tables import main

ROOT = Path(__file__).resolve().parents[1]


class TableProjectionTests(unittest.TestCase):
    def test_table_bodies_match_frozen_exact_data(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'tables'
            with patch('sys.argv',['render_tables.py','--result',
                       str(ROOT/'results/expected/exact-results.json'),
                       '--output',str(output)]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(),0)
            expected = ROOT/'results/expected/tables'
            self.assertEqual({p.name for p in output.glob('*.tex')},
                             {p.name for p in expected.glob('*.tex')})
            for path in output.glob('*.tex'):
                self.assertEqual(path.read_text(),(expected/path.name).read_text(),path.name)

    def test_persistent_table_reports_matching_lifetime_event(self):
        table = (ROOT/'results/expected/tables/semantic-freshness.tex').read_text()
        self.assertIn('3 & 1 & 2 & $7/16$ & $1/2$ & $3/4$',table)
        self.assertIn('5 & 1 & 3 & $721/4096$ & $3/16$ & $7/16$',table)
        rows = [line for line in table.splitlines() if line[:1].isdigit()]
        self.assertEqual(len(rows),8)


if __name__ == '__main__':
    unittest.main()
