"""Self-contained synthetic PDFs and CLI regressions; no private fixtures or network."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote

import pymupdf
import yaml

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from clew_ingest.engine import IngestionEngine, _document_slug, _extract_chapters

LAUNCHER = SKILL_ROOT / "scripts" / "ingest.py"


def make_pdf(path: Path, texts: list[str] | None = None, *, mixed: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pymupdf.open() as doc:
        for text in texts or ["This synthetic prose paragraph has enough ordinary words for extraction."]:
            page = doc.new_page(width=400, height=500)
            page.insert_textbox(pymupdf.Rect(30, 30, 370, 150), text, fontsize=11)
            if mixed:
                page.insert_text((30, 190), "x = 2", fontsize=14)
                page.draw_rect(pymupdf.Rect(30, 240, 150, 285), color=(1, 0, 0))
                with pymupdf.open() as raster:
                    raster_page = raster.new_page(width=80, height=50)
                    raster_page.draw_rect(raster_page.rect, color=(0, 0, 1), fill=(0, 1, 0))
                    image = raster_page.get_pixmap().tobytes("png")
                page.insert_image(pymupdf.Rect(30, 350, 110, 400), stream=image)
        doc.save(path)


def read_artifact(path: Path) -> tuple[dict, str]:
    _, metadata, body = path.read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(metadata), body


class IngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runs = SKILL_ROOT / "tests" / ".runs"
        self.work = self.runs / f"case {uuid.uuid4().hex}"
        self.work.mkdir(parents=True)
        self.cwd = self.work / "unrelated caller directory"
        self.cwd.mkdir()
        self.source = self.work / "source materials"
        self.source.mkdir()
        self.output = self.work / "extracted notes"
        self.assets = self.work / "image assets (review) #1"

    def tearDown(self) -> None:
        shutil.rmtree(self.work)
        try:
            self.runs.rmdir()
        except OSError:
            pass

    def engine(self, **kwargs) -> IngestionEngine:
        return IngestionEngine(str(self.output), str(self.assets), **kwargs)

    def cli(self, *args: object) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env.update({"NO_COLOR": "1", "TERM": "dumb", "PYTHONIOENCODING": "utf-8"})
        return subprocess.run(
            [sys.executable, str(LAUNCHER), *(str(arg) for arg in args)],
            cwd=self.cwd,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=60,
        )

    def assert_links_exist(self, chapter: Path) -> list[Path]:
        links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", chapter.read_text(encoding="utf-8"))
        self.assertTrue(links, "Expected at least one image link")
        assets = []
        for link in links:
            self.assertNotIn("\\", link)
            self.assertNotIn(" ", link)
            image = (chapter.parent / unquote(link)).resolve()
            self.assertTrue(image.is_file(), f"Missing asset: {link}")
            self.assertGreater(image.stat().st_size, 0)
            assets.append(image)
        return assets

    def test_image_first_smoke_with_custom_roots_and_spaces(self):
        pdf = self.source / "Lecture [synthetic] notes.pdf"
        make_pdf(pdf, mixed=True)
        result = self.cli(pdf, "--output", self.output, "--assets", self.assets,
                          "--course", "Synthetic Course", "--domain", "Mathematics")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        chapter = self.output / "lecture-synthetic-notes" / "01-full-document.md"
        metadata, body = read_artifact(chapter)
        self.assertEqual(metadata["course"], "Synthetic Course")
        self.assertEqual(metadata["domains"], ["Mathematics"])
        self.assertEqual(metadata["source"], pdf.name)
        self.assertEqual(metadata["artifacts"]["pages"], 1)
        self.assertEqual(metadata["artifacts"]["images"], 1)
        self.assertGreaterEqual(metadata["artifacts"]["diagrams"], 2)
        self.assertIn("synthetic prose", body)
        self.assertIn("<!-- Page 1 -->", body)
        self.assertIn("Diagram / Formula", body)
        self.assertNotIn("x = 2", body)
        self.assertNotIn("```mermaid", body)
        self.assertNotIn("[!exercise]", body)
        self.assertIn("%20", body)
        self.assertIn("%28", body)
        self.assertIn("%23", body)
        self.assert_links_exist(chapter)

    def test_defaults_from_foreign_cwd_and_150_dpi(self):
        pdf = self.source / "Practice Sheet.pdf"
        make_pdf(pdf, ["Practice problems\nFind a synthetic answer to this example."])
        result = self.cli(pdf)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        chapter = self.cwd / "content" / "practice-sheet" / "01-full-document.md"
        metadata, body = read_artifact(chapter)
        self.assertEqual(metadata["type"], "course-content")
        self.assertEqual(metadata["course"], "General")
        self.assertEqual(metadata["domains"], ["General"])
        self.assertEqual(metadata["concepts"], [])
        self.assertEqual(metadata["chapter_index"], 1)
        self.assertEqual(metadata["chapter_count"], 1)
        self.assertEqual(metadata["artifacts"], {"exercises": 1, "diagrams": 0, "images": 0, "pages": 1})
        self.assertIn("../assets/practice-sheet/page-1-exercise.png", body)
        image = self.assert_links_exist(chapter)[0]
        pixmap = pymupdf.Pixmap(str(image))
        self.assertEqual((pixmap.xres, pixmap.yres), (150, 150))
        self.assertEqual((pixmap.width, pixmap.height), (834, 1042))

    def test_output_option_does_not_change_default_assets(self):
        pdf = self.source / "Independent.pdf"
        make_pdf(pdf, ["Tutorial exercises\nSynthetic exercise."])
        result = self.cli(pdf, "-o", self.output, "-c", "Course", "-d", "Domain")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        chapter = self.output / "independent" / "01-full-document.md"
        image = self.assert_links_exist(chapter)[0]
        self.assertEqual(image.parent, self.cwd / "content" / "assets" / "independent")
        metadata, _ = read_artifact(chapter)
        self.assertEqual(metadata["course"], "Course")
        self.assertEqual(metadata["domains"], ["Domain"])

    def test_contents_offset_and_exercise_chapter_smoke(self):
        pdf = self.source / "Chapters.pdf"
        make_pdf(pdf, [
            "Contents\nFoundations .... 1\nTutorial exercises .... 2",
            "Foundations\nThis paragraph contains enough ordinary words to remain editable prose.",
            "Tutorial exercises\nCompute the result of this synthetic exercise.",
        ])
        with pymupdf.open(pdf) as doc:
            self.assertEqual(_extract_chapters(doc), [("Foundations", 1, 1), ("Tutorial exercises", 2, 2)])
        results = self.engine().ingest_pdf(pdf)
        self.assertEqual(len(results), 2)
        metadata, body = read_artifact(results[0][0])
        self.assertEqual(metadata["chapter_count"], 2)
        self.assertIn("<!-- Page 2 -->", body)
        self.assertEqual(results[1][1]["exercises"], 1)
        self.assert_links_exist(results[1][0])

    def test_contents_merges_entries_on_same_page(self):
        pdf = self.source / "Shared page.pdf"
        make_pdf(pdf, [
            "Contents\nFoundations .... 1\nApplications .... 1",
            "Foundations\nApplications\nThis is synthetic chapter prose for two short sections.",
        ])
        with pymupdf.open(pdf) as doc:
            self.assertEqual(_extract_chapters(doc), [("Foundations / Applications", 1, 1)])

    def test_invalid_contents_is_document_failure(self):
        pdf = self.source / "Bad contents.pdf"
        make_pdf(pdf, ["Contents\nMissing chapter .... 999"])
        result = self.cli(pdf, "-o", self.output, "-a", self.assets)
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside the PDF", " ".join(result.stdout.split()))
        self.assertFalse(list(self.output.rglob("*.md")))

    def test_directory_case_variants_once_nonrecursive(self):
        for name in ["Lower.pdf", "Upper.PDF", "Mixed.PdF"]:
            make_pdf(self.source / name)
        make_pdf(self.source / "nested" / "Hidden.pdf")
        result = self.cli(self.source, "-o", self.output, "-a", self.assets)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("3 document(s)", result.stdout)
        self.assertEqual(result.stdout.count("Ingested:"), 3)
        self.assertEqual(len(list(self.output.rglob("*.md"))), 3)
        self.assertFalse((self.output / "hidden").exists())

    def test_batch_failure_does_not_hide_success_or_return_zero(self):
        (self.source / "A Broken [red].pdf").write_bytes(b"not a PDF")
        make_pdf(self.source / "Z Good.pdf")
        result = self.cli(self.source, "-o", self.output, "-a", self.assets)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Failed A Broken [red].pdf", result.stdout)
        self.assertIn("1 failed document(s)", result.stdout)
        self.assertNotIn("Ingestion complete!", result.stdout)
        self.assertTrue((self.output / "z-good" / "01-full-document.md").is_file())

    def test_missing_non_pdf_and_corrupt_files_fail(self):
        wrong = self.source / "notes.txt"
        wrong.write_text("Not a PDF", encoding="utf-8")
        corrupt = self.source / "broken.pdf"
        corrupt.write_bytes(b"%PDF-1.7\nbroken")
        for path in [self.source / "missing.pdf", wrong, corrupt]:
            with self.subTest(path=path.name):
                result = self.cli(path, "-o", self.output, "-a", self.assets)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_encrypted_pdf_fails_clearly(self):
        pdf = self.source / "Locked.pdf"
        with pymupdf.open() as doc:
            doc.new_page()
            doc.save(pdf, encryption=pymupdf.PDF_ENCRYPT_AES_256,
                     owner_pw="synthetic-owner", user_pw="synthetic-reader")
        result = self.cli(pdf, "-o", self.output, "-a", self.assets)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Password-protected", result.stdout)

    def test_non_pdf_content_with_pdf_suffix_fails(self):
        fake = self.source / "Actually an image.pdf"
        with pymupdf.open() as doc:
            page = doc.new_page()
            fake.write_bytes(page.get_pixmap().tobytes("png"))
        result = self.cli(fake, "-o", self.output, "-a", self.assets)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Not a PDF document", result.stdout)

    def test_empty_directory_warning_preserves_zero(self):
        result = self.cli(self.source, "-o", self.output, "-a", self.assets)
        self.assertEqual(result.returncode, 0)
        self.assertIn("No PDF files", result.stdout)
        self.assertFalse(self.output.exists())

    def test_collision_fails_before_writing(self):
        make_pdf(self.source / "Same Name.pdf")
        make_pdf(self.source / "Same-Name.PDF")
        result = self.cli(self.source, "-o", self.output, "-a", self.assets)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Output name collision", result.stdout)
        self.assertFalse(self.output.exists())

    def test_non_ascii_and_windows_reserved_document_slugs(self):
        self.assertEqual(_document_slug(Path("中文.pdf")), "document")
        self.assertEqual(_document_slug(Path("CON.pdf")), "document-con")
        self.assertEqual(_document_slug(Path("LPT1.pdf")), "document-lpt1")
        pdf = self.source / "中文.pdf"
        make_pdf(pdf)
        results = self.engine().ingest_pdf(pdf)
        self.assertEqual(results[0][0].parent, self.output / "document")

    def test_cross_volume_link_falls_back_to_file_uri(self):
        engine = self.engine()
        asset = self.assets / "document" / "page 1.png"
        with patch("clew_ingest.engine.os.path.relpath", side_effect=ValueError("different drives")):
            self.assertEqual(engine._asset_link(asset, "document"), asset.resolve().as_uri())

    def test_output_setup_failure_is_nonzero(self):
        pdf = self.source / "Good.pdf"
        make_pdf(pdf)
        self.output.write_text("Blocking file", encoding="utf-8")
        result = self.cli(pdf, "-o", self.output, "-a", self.assets)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stdout)

    def test_document_closes_after_success_and_render_error(self):
        pdf = self.source / "Closable.pdf"
        make_pdf(pdf)
        engine = self.engine()
        for fails in [False, True]:
            with self.subTest(fails=fails):
                doc = pymupdf.open(pdf)
                with patch("clew_ingest.engine.pymupdf.open", return_value=doc):
                    if fails:
                        with patch.object(engine, "_render_chapter_pages", side_effect=OSError("synthetic error")):
                            with self.assertRaisesRegex(OSError, "synthetic error"):
                                engine.ingest_pdf(pdf)
                    else:
                        engine.ingest_pdf(pdf)
                self.assertTrue(doc.is_closed)

    def test_help_and_usage_errors(self):
        result = self.cli("--help")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for option in ["--output", "--assets", "--course", "--domain"]:
            self.assertIn(option, result.stdout)
        self.assertEqual(self.cli().returncode, 2)
        self.assertEqual(self.cli("--unknown").returncode, 2)


if __name__ == "__main__":
    unittest.main()
