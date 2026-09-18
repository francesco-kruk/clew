import ctypes
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.courses import storage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="clew-test-")
        self.root = Path(self.temporary.name)
        self.config = self.root / "clone" / ".clew.local.json"
        self.config.parent.mkdir()
        self.patches = [
            patch.object(storage, "ROOT", self.config.parent),
            patch.object(storage, "CONFIG", self.config),
        ]
        for item in self.patches:
            item.start()
        self.addCleanup(self.temporary.cleanup)
        self.addCleanup(lambda: [item.stop() for item in self.patches])

    def test_requires_explicit_external_vault(self):
        with self.assertRaises(storage.CourseError):
            storage.vault_path()
        for invalid in [self.config.parent, self.config.parent / "vault", self.root, Path("relative")]:
            with self.subTest(invalid=invalid), self.assertRaises(storage.CourseError):
                storage.vault_path(invalid)

    def test_configure_preserves_private_sentinels(self):
        vault = self.root / "external vault"
        for name in ["model", "artifacts"]:
            (vault / name).mkdir(parents=True)
            (vault / name / "sentinel").write_bytes(b"private-original")
        storage.configure(vault)
        self.assertEqual(storage.vault_path(), vault.resolve())
        for name in ["model", "artifacts"]:
            self.assertEqual((vault / name / "sentinel").read_bytes(), b"private-original")
        self.assertFalse((vault / ".git").exists())

    def test_git_privacy_and_tracked_conflict(self):
        vault = self.root / "versioned-vault"
        vault.mkdir()
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        (vault / ".gitignore").write_text("keep-me\n")
        storage.configure(vault)
        self.assertIn("keep-me\n", (vault / ".gitignore").read_text())
        self.assertIn("/model/", (vault / ".gitignore").read_text())
        (vault / "model").mkdir()
        (vault / "model" / "private.md").write_text("original")
        subprocess.run(["git", "-C", str(vault), "add", "-f", "model"], check=True)
        with self.assertRaisesRegex(storage.CourseError, "already tracked"):
            storage.configure(vault)
        self.assertEqual((vault / "model" / "private.md").read_text(), "original")

    def test_duplicate_config_rejected(self):
        self.config.write_text('{"version":1,"vault":"one","vault":"two"}')
        with self.assertRaisesRegex(storage.CourseError, "Duplicate"):
            storage.vault_path()

    def test_case_variant_tracked_private_paths_are_rejected(self):
        vault = self.root / "versioned-vault"
        vault.mkdir()
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        (vault / "Model").mkdir()
        (vault / "Model" / "private.md").write_text("original")
        subprocess.run(["git", "-C", str(vault), "add", "Model"], check=True)
        with self.assertRaisesRegex(storage.CourseError, "already tracked"):
            storage.configure(vault)

    def short_path(self, path):
        from ctypes import wintypes

        get_short_path = ctypes.WinDLL("kernel32", use_last_error=True).GetShortPathNameW
        get_short_path.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        get_short_path.restype = wintypes.DWORD
        buffer = ctypes.create_unicode_buffer(32768)
        length = get_short_path(str(path.resolve()), buffer, len(buffer))
        if not length:
            raise ctypes.WinError(ctypes.get_last_error())
        self.assertLess(length, len(buffer))
        result = Path(buffer.value)
        if result == path.resolve():
            self.skipTest("This volume does not provide Windows short-path aliases.")
        return result

    @unittest.skipUnless(os.name == "nt", "Windows short-path aliases")
    def test_short_paths_cannot_bypass_clone_boundary(self):
        clone = self.short_path(self.config.parent)
        for invalid in (clone, clone / "new-vault", clone.parent):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(storage.CourseError, "outside this clone"):
                storage.vault_path(invalid)

    @unittest.skipUnless(os.name == "nt", "Windows short-path aliases")
    def test_short_path_vault_preserves_git_privacy_checks(self):
        vault = self.root / "versioned external vault"
        vault.mkdir()
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        alias = self.short_path(vault)
        self.assertEqual(storage.configure(alias), vault.resolve())
        self.assertEqual(storage.vault_path(), vault.resolve())
        self.assertIn("/model/", (vault / ".gitignore").read_text())
        (vault / "model").mkdir()
        (vault / "model" / "private.md").write_text("original")
        subprocess.run(["git", "-C", str(vault), "add", "-f", "model"], check=True)
        with self.assertRaisesRegex(storage.CourseError, "already tracked"):
            storage.protect_private_paths(alias)
        self.assertEqual((vault / "model" / "private.md").read_text(), "original")


if __name__ == "__main__":
    unittest.main()
