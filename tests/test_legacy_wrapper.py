import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ingest import cli


class LegacyWrapperTests(unittest.TestCase):
    def test_missing_restore_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(cli, "SCRIPT", Path(directory) / "missing.py"):
                error = io.StringIO()
                with contextlib.redirect_stderr(error):
                    self.assertEqual(cli.main(), 1)
                self.assertIn("apm install --frozen", error.getvalue())

    def test_dependency_error_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "ingest.py"
            script.write_text("import clew_intentionally_missing_pdf_dependency\n")
            with patch.object(cli, "SCRIPT", script), contextlib.redirect_stderr(io.StringIO()) as error:
                self.assertEqual(cli.main(), 1)
            self.assertIn("requirements.txt", error.getvalue())

    def test_original_arguments_and_process_state_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "ingest.py"
            script.write_text("import sys\nassert sys.argv[1:] == ['a b.pdf', '--course', 'Original']\n")
            arguments = ["legacy", "a b.pdf", "--course", "Original"]
            previous_path = sys.path[:]
            with patch.object(cli, "SCRIPT", script), patch.object(sys, "argv", arguments[:]):
                self.assertEqual(cli.main(), 0)
                self.assertEqual(sys.argv, arguments)
                self.assertEqual(sys.path, previous_path)

    def test_engine_failure_status_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "ingest.py"
            script.write_text("raise SystemExit(7)\n")
            with patch.object(cli, "SCRIPT", script), self.assertRaises(SystemExit) as result:
                cli.main()
            self.assertEqual(result.exception.code, 7)
