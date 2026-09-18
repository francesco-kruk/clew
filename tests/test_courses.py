import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fixtures import COURSE, PREFIX, rehash, write_package
from src.courses import cli, importer, source, storage, validation
from src.courses.storage import CourseError


class ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = validation.load_validator()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="clew-original-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.checkout = self.root / "teacher source"
        self.checkout.mkdir()
        self.package = write_package(self.checkout)
        self.vault = self.root / "student vault"
        self.vault.mkdir()
        self.sentinels = []
        for directory in ("model", "artifacts"):
            path = self.vault / directory / "private.md"
            path.parent.mkdir()
            path.write_bytes(b"PRIVATE original synthetic sentinel\x00\xff")
            self.sentinels.append(path)
        self.addCleanup(self.assert_private_unchanged)
        self.git("init", "--quiet")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "user.email", "tests@example.invalid")
        self.git("config", "user.name", "Original fixture")
        self.commit()

    def assert_private_unchanged(self):
        for path in self.sentinels:
            self.assertEqual(path.read_bytes(), b"PRIVATE original synthetic sentinel\x00\xff")

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.checkout), *arguments],
                              check=True, capture_output=True).stdout.decode().strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Original fixture")
        return self.git("rev-parse", "HEAD")

    def install(self, ref=None):
        with source.open_source(checkout=self.checkout, ref=ref) as snapshot:
            return importer.import_course(snapshot, "original-examples", self.vault, self.validator)

    def manifest(self, change):
        path = self.package / "course-package.json"
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))
        self.commit()

    def test_shared_validator_accepts_original_fixture(self):
        result = self.validator.validate_package(self.package)
        self.assertTrue(result["ok"], result["errors"])

    def test_install_then_exact_noop(self):
        first = self.install()
        self.assertEqual(first["status"], "installed")
        final = self.vault / PREFIX / "hub.md"
        modified = final.stat().st_mtime_ns
        self.assertEqual(self.install()["status"], "unchanged")
        self.assertEqual(final.stat().st_mtime_ns, modified)
        receipt = storage.read_json(self.vault / ".clew" / "imports" / "original-examples.json")
        self.assertEqual(receipt["commit"], first["commit"])
        self.assertEqual(importer.inventory(self.vault / PREFIX), receipt["files"])

    def test_import_never_opens_private_state(self):
        original = Path.open

        def guarded(path, *args, **kwargs):
            if path.is_relative_to(self.vault):
                relative = path.relative_to(self.vault)
                if relative.parts and relative.parts[0] in ("model", "artifacts"):
                    self.fail("Importer attempted to open private state")
            return original(path, *args, **kwargs)

        with patch.object(Path, "open", guarded):
            self.assertEqual(self.install()["status"], "installed")
            self.assertEqual(self.install()["status"], "unchanged")

    def test_changed_revision_is_staged_not_activated(self):
        first = self.install()
        original = (self.vault / PREFIX / "hub.md").read_bytes()
        with (self.package / "hub.md").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("\nRevised original text.\n")
        rehash(self.package)
        revision = self.commit()
        result = self.install()
        self.assertEqual(result["status"], "staged")
        self.assertEqual(result["commit"], revision)
        self.assertEqual((self.vault / PREFIX / "hub.md").read_bytes(), original)
        self.assertEqual(Path(result["path"]).parts[-2:], ("courses", COURSE))
        receipt = storage.read_json(self.vault / ".clew" / "imports" / "original-examples.json")
        self.assertEqual(receipt["commit"], first["commit"])
        self.assertEqual(self.install()["status"], "staged")

    def test_dirty_and_unrecognized_existing_courses_conflict(self):
        self.install()
        (self.vault / PREFIX / "hub.md").write_text("Student edits")
        with self.assertRaisesRegex(CourseError, "Locally modified"):
            self.install()
        (self.vault / ".clew" / "imports" / "original-examples.json").unlink()
        with self.assertRaisesRegex(CourseError, "Unrecognized"):
            self.install()
        self.assertEqual((self.vault / PREFIX / "hub.md").read_text(), "Student edits")

    def test_added_local_file_conflicts(self):
        self.install()
        (self.vault / PREFIX / "personal.md").write_text("Do not replace")
        with self.assertRaisesRegex(CourseError, "Locally modified"):
            self.install()

    def test_unicode_paths_and_headings_are_preserved(self):
        old = self.package / "chapters" / "EX - 01.md"
        new = self.package / "chapters" / "EX - Caf\u00e9.md"
        old.rename(new)
        for path in (self.package / "hub.md", self.package / "map.canvas", new):
            text = path.read_text(encoding="utf-8").replace("EX - 01", "EX - Caf\u00e9")
            text = text.replace("Counting", "Counting \u03b1")
            path.write_text(text, encoding="utf-8", newline="\n")
        rehash(self.package)
        self.commit()
        self.assertEqual(self.install()["status"], "installed")
        installed = self.vault / PREFIX / "chapters" / new.name
        self.assertEqual(installed.read_bytes(), new.read_bytes())

    def test_hash_mismatch_and_pending_rights_fail(self):
        self.manifest(lambda value: value["files"][0].update(sha256="0" * 64))
        with self.assertRaisesRegex(CourseError, "validation"):
            self.install()
        rehash(self.package)
        self.manifest(lambda value: value["rights"].update(status="pending"))
        with self.assertRaisesRegex(CourseError, "validation"):
            self.install()
        self.assertFalse((self.vault / PREFIX).exists())

    def test_malicious_inventory_and_malformed_catalog_fail(self):
        self.manifest(lambda value: value["files"].append({"path": "../../model/private.md", "sha256": "0" * 64}))
        with self.assertRaisesRegex(CourseError, "validation"):
            self.install()
        (self.checkout / "catalog.json").write_text('{"schema_version":99,"courses":[]}')
        self.commit()
        with self.assertRaisesRegex(CourseError, "Catalog.*validation"):
            self.install()

    def test_executable_and_private_inventory_fail(self):
        (self.package / "run.py").write_text("raise RuntimeError('Never execute')\n")
        rehash(self.package)
        self.commit()
        with self.assertRaisesRegex(CourseError, "validation"):
            self.install()
        (self.package / "run.py").unlink()
        (self.package / "model").mkdir()
        (self.package / "model" / "private.md").write_text("Not permitted")
        rehash(self.package)
        self.commit()
        with self.assertRaisesRegex(CourseError, "validation"):
            self.install()

    def test_canvas_path_escape_fails(self):
        (self.package / "map.canvas").write_text(json.dumps({"nodes": [
            {"id": "one", "type": "file", "file": "model/private.md",
             "x": 0, "y": 0, "width": 100, "height": 100}], "edges": []}))
        rehash(self.package)
        self.commit()
        with self.assertRaisesRegex(CourseError, "validation"):
            self.install()

    def test_failure_before_rename_leaves_no_final_and_retry_recovers(self):
        with patch.object(importer.os, "rename", side_effect=OSError("simulated interrupted rename")):
            with self.assertRaisesRegex(OSError, "interrupted"):
                self.install()
        self.assertFalse((self.vault / PREFIX).exists())
        self.assertFalse((self.vault / ".clew" / "imports" / "original-examples.json").exists())
        self.assertEqual(self.install()["status"], "installed")

    def test_failure_after_rename_recovers_receipt_without_replacement(self):
        original = importer.atomic_json

        def interrupt(path, value):
            if path.name == "original-examples.json":
                raise OSError("simulated receipt interruption")
            return original(path, value)

        with patch.object(importer, "atomic_json", side_effect=interrupt):
            with self.assertRaisesRegex(OSError, "interruption"):
                self.install()
        self.assertTrue((self.vault / PREFIX / "hub.md").is_file())
        self.assertFalse((self.vault / ".clew" / "imports" / "original-examples.json").exists())
        self.assertEqual(self.install()["status"], "unchanged")
        self.assertFalse((self.vault / ".clew" / "imports" / "original-examples.pending.json").exists())

    def test_explicit_commit_ignores_working_tree_and_bad_ref_fails(self):
        commit = self.git("rev-parse", "HEAD")
        (self.package / "hub.md").write_text("Uncommitted, must never be imported")
        result = self.install(commit)
        self.assertEqual(result["commit"], commit)
        self.assertNotIn("Uncommitted", (self.vault / PREFIX / "hub.md").read_text())
        with self.assertRaises(CourseError):
            self.install("refs/heads/does-not-exist")

    def test_ref_is_resolved_once_before_any_catalog_or_file_read(self):
        with source.open_source(checkout=self.checkout) as snapshot:
            commit = snapshot.commit
            with (self.package / "hub.md").open("a", newline="\n") as stream:
                stream.write("\nNew ref target.\n")
            rehash(self.package)
            self.assertNotEqual(self.commit(), commit)
            result = importer.import_course(snapshot, "original-examples", self.vault, self.validator)
        self.assertEqual(result["commit"], commit)
        self.assertNotIn("New ref target", (self.vault / PREFIX / "hub.md").read_text())

    def test_pending_receipt_after_complete_install_is_reconciled(self):
        self.install()
        directory = self.vault / ".clew" / "imports"
        receipt = storage.read_json(directory / "original-examples.json")
        storage.atomic_json(directory / "original-examples.pending.json", receipt)
        self.assertEqual(self.install()["status"], "unchanged")
        self.assertFalse((directory / "original-examples.pending.json").exists())

    def test_interrupted_install_does_not_adopt_student_edits(self):
        original = importer.atomic_json

        def interrupt(path, value):
            if path.name == "original-examples.json":
                raise OSError("simulated receipt interruption")
            return original(path, value)

        with patch.object(importer, "atomic_json", side_effect=interrupt), self.assertRaises(OSError):
            self.install()
        (self.vault / PREFIX / "hub.md").write_text("Student work after interruption")
        with self.assertRaisesRegex(CourseError, "Interrupted install conflicts"):
            self.install()
        self.assertEqual((self.vault / PREFIX / "hub.md").read_text(), "Student work after interruption")

    def test_symlink_and_junction_destinations_rejected(self):
        target = self.root / "outside"
        target.mkdir()
        courses = self.vault / "courses"
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(courses), str(target)],
                           check=True, capture_output=True)
        else:
            courses.symlink_to(target, target_is_directory=True)
        try:
            with self.assertRaisesRegex(CourseError, "Symlink/reparse"):
                self.install()
            self.assertEqual(list(target.iterdir()), [])
        finally:
            if os.name == "nt":
                courses.rmdir()
            else:
                courses.unlink()

    def test_source_symlink_is_not_followed(self):
        # Git-index symlinks work even on Windows without symlink privilege.
        result = subprocess.run(["git", "-C", str(self.checkout), "hash-object", "-w", "--stdin"],
                                input=b"../../../private.md", capture_output=True, check=True)
        oid = result.stdout.decode().strip()
        self.git("update-index", "--add", "--cacheinfo", "120000", oid, PREFIX + "/escape.md")
        self.git("commit", "--quiet", "-m", "Synthetic unsafe symlink")
        with self.assertRaisesRegex(CourseError, "regular files"):
            self.install()

    def test_case_collision_in_source_index_is_rejected(self):
        oid = self.git("rev-parse", "HEAD:" + PREFIX + "/hub.md")
        self.git("update-index", "--add", "--cacheinfo", "100644", oid, PREFIX + "/HUB.md")
        self.git("commit", "--quiet", "-m", "Synthetic case collision")
        with self.assertRaisesRegex(CourseError, "collision"):
            self.install()

    def test_unconfigured_import_cli_fails_before_source_access(self):
        with patch.object(storage, "CONFIG", self.root / "missing-config.json"):
            with patch.object(cli, "open_source") as opened:
                with contextlib.redirect_stderr(io.StringIO()) as error:
                    self.assertEqual(cli.main(["import", "original-examples"]), 1)
                opened.assert_not_called()
                self.assertIn("configure", error.getvalue())

    def test_catalog_unavailable_is_actionable(self):
        (self.checkout / "catalog.json").unlink()
        self.git("add", "-u")
        self.git("commit", "--quiet", "-m", "Missing catalog")
        with self.assertRaisesRegex(CourseError, "Catalog unavailable"):
            self.install()


class PathTests(unittest.TestCase):
    def test_unsafe_paths(self):
        for path in ("../file", "/tmp/file", "C:/file", "\\\\host\\share", "a//b",
                     "a/../b", "a\\b", "NUL.md", "COM1", "a. ", "a:b", "a/"):
            with self.subTest(path=path), self.assertRaises(CourseError):
                validation.safe_relative(path)

    def test_spaces_and_unicode_are_preserved(self):
        value = "courses/Original Examples/chapters/Caf\u00e9.md"
        self.assertEqual(validation.safe_relative(value), value)

    def test_invalid_remote_source_and_ref(self):
        for repository, ref in (("https://untrusted.invalid/repo", "main"),
                                ("owner/repo", "--upload-pack=malicious"),
                                ("owner/repo", "main bad")):
            with self.subTest(repository=repository, ref=ref), self.assertRaises(CourseError):
                with source.open_source(repository, ref):
                    self.fail("Invalid source was accepted")

    def test_failed_download_has_nonzero_error(self):
        completed = subprocess.CompletedProcess([], 128, b"", b"synthetic network failure")
        with patch.object(source.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(CourseError, "network failure"):
                with source.open_source():
                    self.fail("Failed download was accepted")
