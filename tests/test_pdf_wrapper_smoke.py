"""Optional legacy-PDF integration; normal student tests need no PDF libraries."""

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.ingest.cli import SCRIPT

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec("pymupdf"), "optional PDF dependencies are not installed")
class PdfWrapperSmokeTests(unittest.TestCase):
    def test_module_wrapper_matches_installed_script(self):
        import pymupdf

        with tempfile.TemporaryDirectory(prefix="clew-original-pdf-") as directory:
            work = Path(directory)
            pdf = work / "Original lesson.pdf"
            with pymupdf.open() as document:
                page = document.new_page()
                page.insert_text((40, 40), "An original synthetic lesson: one blue token and one red token.")
                page.draw_rect(pymupdf.Rect(40, 90, 160, 140), color=(1, 0, 0))
                document.save(pdf)
            environment = os.environ.copy()
            environment.update({"NO_COLOR": "1", "TERM": "dumb", "PYTHONIOENCODING": "utf-8"})
            outputs = []
            for name, command in [
                ("wrapper", [sys.executable, "-m", "src.ingest.cli"]),
                ("installed", [sys.executable, str(SCRIPT)]),
            ]:
                output = work / name / "notes"
                assets = work / name / "assets"
                result = subprocess.run(
                    [*command, str(pdf), "--output", str(output), "--assets", str(assets),
                     "--course", "Original lesson", "--domain", "Mathematics"],
                    cwd=ROOT if name == "wrapper" else work,
                    env=environment, capture_output=True, text=True, encoding="utf-8", timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                outputs.append({path.relative_to(work / name).as_posix(): path.read_bytes()
                                for path in (work / name).rglob("*") if path.is_file()})
            self.assertTrue(any(path.endswith(".md") for path in outputs[0]))
            self.assertTrue(any(path.endswith(".png") for path in outputs[0]))
            self.assertEqual(outputs[0], outputs[1])
