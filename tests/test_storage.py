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
        self.assertEqual(storage.vault_path(), vault)
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


if __name__ == "__main__":
    unittest.main()
