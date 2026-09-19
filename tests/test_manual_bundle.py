"""Original manually copied notes, with no package metadata or prescribed layout."""

import base64
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.vault import storage


class ManualBundleTests(unittest.TestCase):
    def test_arbitrary_copied_bundle_is_unchanged_and_not_read(self):
        with tempfile.TemporaryDirectory(prefix="clew-manual-bundle-") as temporary:
            root = Path(temporary).resolve()
            clone, vault, teacher = root / "clone", root / "external vault", root / "teacher bundle"
            clone.mkdir()
            vault.mkdir()
            (teacher / "notes").mkdir(parents=True)
            (teacher / "assets").mkdir()
            (teacher / "index.md").write_text("# Original notes\n[Practice](notes/practice.md)\n", encoding="utf-8")
            (teacher / "notes" / "practice.md").write_text(
                "# Practice\nYesterday I walked to the park.\n![Marker](../assets/marker.png)\n",
                encoding="utf-8",
            )
            (teacher / "assets" / "marker.png").write_bytes(base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="
            ))
            copied = vault / "English practice pack"
            shutil.copytree(teacher, copied)
            snapshot = {p.relative_to(vault): (p.read_bytes(), p.stat().st_mtime_ns)
                        for p in vault.rglob("*") if p.is_file()}
            opened = Path.open

            def forbid_vault_reads(path, *args, **kwargs):
                if path.is_relative_to(vault):
                    self.fail("Setup opened copied course content")
                return opened(path, *args, **kwargs)

            with patch.object(storage, "ROOT", clone), patch.object(storage, "CONFIG", clone / ".clew.local.json"):
                with patch.object(Path, "open", forbid_vault_reads):
                    configured = storage.configure(vault)
                    self.assertEqual(configured, storage.status())
                    self.assertEqual(configured, storage.configure(vault))
            after = {p.relative_to(vault): (p.read_bytes(), p.stat().st_mtime_ns)
                     for p in vault.rglob("*") if p.is_file()}
            self.assertEqual(after, snapshot)
            self.assertEqual(configured["existing_private_paths"], [])
            self.assertEqual({p.name for p in vault.iterdir()}, {"English practice pack"})
            self.assertTrue((copied / "notes" / ".." / "assets" / "marker.png").is_file())
