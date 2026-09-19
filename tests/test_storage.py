import contextlib
import ctypes
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.vault import cli, storage


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
        with self.assertRaises(storage.VaultError):
            storage.vault_path()
        for invalid in [self.config.parent, self.config.parent / "vault", self.root, Path("relative")]:
            with self.subTest(invalid=invalid), self.assertRaises(storage.VaultError):
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
        with self.assertRaisesRegex(storage.VaultError, "already tracked"):
            storage.configure(vault)
        self.assertEqual((vault / "model" / "private.md").read_text(), "original")

    def test_duplicate_config_rejected(self):
        self.config.write_text('{"version":1,"vault":"one","vault":"two"}')
        with self.assertRaisesRegex(storage.VaultError, "Duplicate"):
            storage.vault_path()

    def test_case_variant_tracked_private_paths_are_rejected(self):
        vault = self.root / "versioned-vault"
        vault.mkdir()
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        (vault / "Model").mkdir()
        (vault / "Model" / "private.md").write_text("original")
        subprocess.run(["git", "-C", str(vault), "add", "Model"], check=True)
        with self.assertRaisesRegex(storage.VaultError, "already tracked"):
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
            with self.subTest(invalid=invalid), self.assertRaisesRegex(storage.VaultError, "outside this clone"):
                storage.vault_path(invalid)

    @unittest.skipUnless(os.name == "nt", "Windows short-path aliases")
    def test_short_path_vault_preserves_git_privacy_checks(self):
        vault = self.root / "versioned external vault"
        vault.mkdir()
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        alias = self.short_path(vault)
        self.assertEqual(storage.configure(alias)["vault"], str(vault.resolve()))
        self.assertEqual(storage.vault_path(), vault.resolve())
        self.assertIn("/model/", (vault / ".gitignore").read_text())
        (vault / "model").mkdir()
        (vault / "model" / "private.md").write_text("original")
        subprocess.run(["git", "-C", str(vault), "add", "-f", "model"], check=True)
        with self.assertRaisesRegex(storage.VaultError, "already tracked"):
            storage.protect_private_paths(alias)
        self.assertEqual((vault / "model" / "private.md").read_text(), "original")

    def test_missing_vault_is_not_created(self):
        path = self.root / "not created by Clew"
        with self.assertRaisesRegex(storage.VaultError, "does not exist"):
            storage.configure(path)
        self.assertFalse(path.exists())
        self.assertFalse(self.config.exists())

    def test_file_cannot_be_selected_as_vault(self):
        path = self.root / "a file.md"
        path.write_text("original")
        with self.assertRaisesRegex(storage.VaultError, "not a directory"):
            storage.configure(path)
        self.assertEqual(path.read_text(), "original")

    def test_malformed_settings_fail_without_rewriting(self):
        settings = ['[]', '{bad', '{"version":true,"vault":"x"}',
                    '{"version":2,"vault":"x"}', '{"version":1,"vault":null}',
                    '{"vault":"x"}', '{"version":1,"vault":"relative"}',
                    '{"version":1,"vault":"x","extra":true}']
        for content in settings:
            self.config.write_text(content)
            with self.subTest(content=content), self.assertRaises(storage.VaultError):
                storage.status()
            self.assertEqual(self.config.read_text(), content)

    def test_explicit_configuration_repairs_invalid_local_setting(self):
        self.config.write_text("{broken old local setting")
        vault = self.root / "my vault"
        vault.mkdir()
        storage.configure(vault)
        self.assertEqual(storage.status()["vault"], str(vault.resolve()))

    def test_status_and_repeated_configuration_are_idempotent(self):
        vault = self.root / "space containing vault"
        vault.mkdir()
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        first = storage.configure(vault)
        config_time = self.config.stat().st_mtime_ns
        ignore = vault / ".gitignore"
        ignore_bytes, ignore_time = ignore.read_bytes(), ignore.stat().st_mtime_ns
        self.assertEqual(storage.status(), first)
        self.assertEqual(storage.configure(vault), first)
        self.assertEqual(config_time, self.config.stat().st_mtime_ns)
        self.assertEqual(ignore_time, ignore.stat().st_mtime_ns)
        self.assertEqual(ignore_bytes, ignore.read_bytes())
        self.assertFalse((vault / "model").exists())
        self.assertFalse((vault / "artifacts").exists())

    def test_status_reports_missing_ignores_without_writing(self):
        vault = self.root / "existing vault"
        vault.mkdir()
        storage.configure(vault)
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        result = storage.status()
        self.assertEqual(result["git"]["ignore_rules_missing"], ["/model/", "/artifacts/"])
        self.assertTrue(result["warnings"])
        self.assertFalse((vault / ".gitignore").exists())

    def test_configure_preserves_ignore_bytes(self):
        vault = self.root / "versioned vault"
        vault.mkdir()
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        ignore = vault / ".gitignore"
        original = b"keep-this\r\n# original line endings\r\n"
        ignore.write_bytes(original)
        storage.configure(vault)
        self.assertTrue(ignore.read_bytes().startswith(original))

    def test_existing_negation_cannot_defeat_private_ignore_rules(self):
        vault = self.root / "versioned vault"
        vault.mkdir()
        subprocess.run(["git", "init", "--quiet", str(vault)], check=True)
        ignore = vault / ".gitignore"
        original = b"/model/\n/artifacts/\n!/model/\n!/artifacts/\n"
        ignore.write_bytes(original)
        result = storage.configure(vault)
        self.assertEqual(result["git"]["ignore_rules_missing"], [])
        self.assertTrue(ignore.read_bytes().startswith(original))
        self.assertEqual(storage.status()["git"]["ignore_rules_missing"], [])
        for name in ("model/", "artifacts/"):
            result = subprocess.run(["git", "-C", str(vault), "check-ignore", "--no-index", name],
                                    capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_reserved_file_or_directory_is_reported_not_adopted(self):
        vault = self.root / "existing vault"
        vault.mkdir()
        (vault / "Model").write_bytes(b"teacher's file named Model")
        (vault / "artifacts").mkdir()
        (vault / "artifacts" / "example.md").write_bytes(b"original")
        opened = Path.open

        def forbid_reserved_reads(path, *args, **kwargs):
            if path.is_relative_to(vault):
                parts = path.relative_to(vault).parts
                if parts and parts[0].casefold() in storage.PRIVATE:
                    self.fail("Configuration read reserved-path contents")
            return opened(path, *args, **kwargs)

        with patch.object(Path, "open", forbid_reserved_reads):
            result = storage.configure(vault)
            self.assertEqual(result, storage.status())
        self.assertEqual(result["existing_private_paths"], ["Model", "artifacts"])
        self.assertTrue(result["warnings"])
        self.assertEqual((vault / "Model").read_bytes(), b"teacher's file named Model")
        self.assertEqual((vault / "artifacts" / "example.md").read_bytes(), b"original")

    def test_git_privacy_check_handles_nested_vault(self):
        repository = self.root / "versioned parent"
        repository.mkdir()
        subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
        vault = repository / "nested vault"
        vault.mkdir()
        storage.configure(vault)
        (vault / "model").mkdir()
        (vault / "model" / "private.md").write_text("original")
        subprocess.run(["git", "-C", str(repository), "add", "-f", "."], check=True)
        with self.assertRaisesRegex(storage.VaultError, "already tracked"):
            storage.status()

    def test_config_write_failure_preserves_previous_setting(self):
        vault = self.root / "my vault"
        vault.mkdir()
        self.config.write_bytes(b"original local setting")
        with patch.object(storage.os, "replace", side_effect=PermissionError("simulated denied config write")):
            with self.assertRaises(PermissionError):
                storage.configure(vault)
        self.assertEqual(self.config.read_bytes(), b"original local setting")
        self.assertEqual(list(self.config.parent.glob(".clew-write-*")), [])

    def test_directory_permission_error_is_actionable(self):
        vault = self.root / "my vault"
        vault.mkdir()
        with patch.object(Path, "iterdir", side_effect=PermissionError("simulated denied vault access")):
            with contextlib.redirect_stderr(io.StringIO()) as error:
                self.assertEqual(cli.main(["configure", "--vault", str(vault)]), 1)
        self.assertIn("denied vault access", error.getvalue())
        self.assertFalse(self.config.exists())

    def test_missing_git_cannot_skip_private_tracking_protection(self):
        vault = self.root / "my vault"
        vault.mkdir()
        with patch.object(storage.subprocess, "run", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(storage.VaultError, "Git is required"):
                storage.configure(vault)
        self.assertFalse(self.config.exists())

    def test_cli_json_and_nonzero_absent_config(self):
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(cli.main(["status"]), 1)
        self.assertIn("configure", error.getvalue())
        vault = self.root / "my vault"
        vault.mkdir()
        for command in (["configure", "--vault", str(vault)], ["status"]):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(cli.main(command), 0)
            self.assertEqual(json.loads(output.getvalue())["vault"], str(vault.resolve()))

    def test_missing_config_permission_is_reported(self):
        self.config.write_text('{"version":1,"vault":"original"}')
        with patch.object(Path, "read_text", side_effect=PermissionError("simulated unreadable config")):
            with contextlib.redirect_stderr(io.StringIO()) as error:
                self.assertEqual(cli.main(["status"]), 1)
        self.assertIn("unreadable config", error.getvalue())

    def test_junction_or_symlink_vault_is_rejected_before_resolution(self):
        target = self.root / "real vault"
        target.mkdir()
        alias = self.root / "linked vault"
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(target)],
                           check=True, capture_output=True)
        else:
            alias.symlink_to(target, target_is_directory=True)
        try:
            with self.assertRaisesRegex(storage.VaultError, "Symlink/reparse"):
                storage.configure(alias)
            self.assertEqual(list(target.iterdir()), [])
        finally:
            if os.name == "nt":
                alias.rmdir()
            else:
                alias.unlink()


if __name__ == "__main__":
    unittest.main()
