import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fixtures import make_course, refresh_manifest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_course.py"
spec = importlib.util.spec_from_file_location("validate_course", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CourseValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="clew synthetic ")
        self.root = Path(self.temp.name)
        self.package = make_course(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def result(self, mode="publish"):
        return validator.validate_package(self.package, mode)

    def assertInvalid(self, code):
        result = self.result()
        self.assertFalse(result["ok"], result)
        self.assertIn(code, {entry["code"] for entry in result["errors"]}, result)

    def edit(self, name, before, after):
        path = self.package / name
        path.write_text(path.read_text(encoding="utf-8").replace(before, after), encoding="utf-8")
        refresh_manifest(self.package)

    def test_valid_package_and_catalog(self):
        self.assertTrue(self.result()["ok"], self.result())
        result = validator.validate_catalog(self.root / "catalog.json")
        self.assertTrue(result["ok"], result)

    def test_cli_from_unrelated_directory(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--package", str(self.package)],
            cwd=self.root, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_draft_pending_not_publishable(self):
        self.package = make_course(self.root, rights="pending")
        self.assertTrue(self.result("draft")["ok"], self.result("draft"))
        self.assertInvalid("rights")
        self.assertFalse(validator.validate_catalog(self.root / "catalog.json")["ok"])

    def test_catalog_only_does_not_read_packages(self):
        (self.package / "hub.md").unlink()
        result = validator.validate_catalog(self.root / "catalog.json", packages=False)
        self.assertTrue(result["ok"], result)
        self.assertFalse(validator.validate_catalog(self.root / "catalog.json")["ok"])

    def test_empty_catalog(self):
        (self.root / "catalog.json").write_text('{"schema_version":1,"courses":[]}', encoding="utf-8")
        self.assertTrue(validator.validate_catalog(self.root / "catalog.json")["ok"])

    def test_catalog_identity_mismatch(self):
        path = self.root / "catalog.json"
        text = path.read_text()
        path.write_text(text.replace('"synthetic-mechanics"', '"wrong"'))
        self.assertFalse(validator.validate_catalog(path)["ok"])

    def test_hash_mismatch(self):
        with (self.package / "hub.md").open("a", encoding="utf-8") as stream:
            stream.write("\nChanged\n")
        self.assertInvalid("hash")

    def test_missing_inventory_file(self):
        (self.package / "hub.md").unlink()
        self.assertInvalid("inventory")

    def test_uninventoried_file(self):
        (self.package / "extra.txt").write_text("extra")
        self.assertInvalid("inventory")

    def test_manifest_cannot_inventory_itself(self):
        path = self.package / "course-package.json"
        data = json.loads(path.read_text())
        data["files"].append({"path": "course-package.json", "sha256": "0" * 64})
        path.write_text(json.dumps(data))
        self.assertInvalid("inventory")

    def test_reject_unsafe_manifest_paths(self):
        path = self.package / "course-package.json"
        original = json.loads(path.read_text())
        for unsafe in ("../outside", "/absolute", "C:/escape", "\\\\server\\share",
                       "CON.md", "LPT1.txt", "trailing.", "trailing ", "a//b", "a\\b",
                       "a:b.md", ".git/config", "bad|name.md", "bad#name.md"):
            with self.subTest(path=unsafe):
                data = dict(original)
                data["files"] = [{"path": unsafe, "sha256": "0" * 64}]
                path.write_text(json.dumps(data))
                self.assertInvalid("path")

    def test_private_and_tooling_exclusions(self):
        for name in ("model/private.md", "scripts/run.py", "apm_modules/cache.json"):
            with self.subTest(path=name):
                path = self.package / name
                path.parent.mkdir(exist_ok=True)
                path.write_text("private synthetic sentinel")
                refresh_manifest(self.package)
                self.assertInvalid("excluded")
                path.unlink()
                path.parent.rmdir()
        refresh_manifest(self.package)

    def test_case_colliding_inventory(self):
        path = self.package / "course-package.json"
        data = json.loads(path.read_text())
        data["files"].append({"path": "HUB.md", "sha256": "0" * 64})
        path.write_text(json.dumps(data))
        self.assertInvalid("collision")

    def test_symlink_rejected(self):
        link = self.package / "leak.txt"
        try:
            link.symlink_to(self.package / "hub.md")
        except OSError as exc:
            self.skipTest(f"Host cannot create test symlinks: {exc}")
        self.assertInvalid("path")

    def test_missing_heading(self):
        self.edit("hub.md", "#Distance]]", "#Absent]]")
        self.assertInvalid("anchor")

    def test_duplicate_heading_is_ambiguous(self):
        chapter = self.package / "chapters" / "SYN - 01 - Motion.md"
        with chapter.open("a") as stream:
            stream.write("\n## Distance\nDuplicate.\n")
        refresh_manifest(self.package)
        self.assertInvalid("anchor")

    def test_block_anchor(self):
        self.edit("hub.md", "#Distance]]", "#^distance]]")
        self.assertTrue(self.result()["ok"], self.result())

    def test_markdown_space_paths_and_fragment(self):
        self.edit("hub.md", "[[courses/Synthetic mechanics/Map.canvas]]",
                  "[Map](<Map.canvas>)")
        self.assertTrue(self.result()["ok"], self.result())

    def test_reference_markdown_target(self):
        self.edit("hub.md", "[[courses/Synthetic mechanics/Map.canvas]]",
                  "[Map][map]\n\n[map]: <Map.canvas>")
        self.assertTrue(self.result()["ok"], self.result())

    def test_markdown_missing_target(self):
        self.edit("hub.md", "## Resources", "[lost](missing.md)\n\n## Resources")
        self.assertInvalid("link")

    def test_link_escape(self):
        self.edit("hub.md", "## Resources", "[escape](../../private.md)\n\n## Resources")
        self.assertInvalid("link")

    def test_ambiguous_basename(self):
        other = self.package / "reports" / "SYN - 01 - Motion.md"
        other.write_text("# Historical duplicate\n")
        self.edit("hub.md", "courses/Synthetic mechanics/chapters/SYN - 01 - Motion",
                  "SYN - 01 - Motion")
        self.assertInvalid("link")

    def test_canvas_vault_prefix_required(self):
        self.edit("Map.canvas", "courses/Synthetic mechanics/chapters/", "chapters/")
        self.assertInvalid("link")

    def test_uppercase_canvas_extension_is_validated(self):
        (self.package / "Map.canvas").rename(self.package / "Map.CANVAS")
        self.edit("hub.md", "Map.canvas", "Map.CANVAS")
        self.edit("Map.CANVAS", "courses/Synthetic mechanics/chapters/", "chapters/")
        self.assertInvalid("link")

    def test_canvas_invalid_edge_returns_report(self):
        path = self.package / "Map.canvas"
        data = json.loads(path.read_text())
        data["edges"] = [{"id": "edge", "fromNode": [], "toNode": "chapter"}]
        path.write_text(json.dumps(data))
        refresh_manifest(self.package)
        self.assertInvalid("canvas")

    def test_orphan_file(self):
        (self.package / "orphan.txt").write_text("not reached")
        refresh_manifest(self.package)
        self.assertInvalid("closure")

    def test_hub_chapter_order_exactly_once(self):
        self.edit("hub.md", "## Concept index",
                  "2. [[courses/Synthetic mechanics/chapters/SYN - 01 - Motion]]\n\n## Concept index")
        self.assertInvalid("metadata")

    def test_required_domain_list(self):
        self.edit("hub.md", "primary_domains: [Physics]", "primary_domains: Physics")
        self.assertInvalid("metadata")

    def test_concept_location_requires_authoritative_anchor(self):
        self.edit("hub.md", "#Distance]]", "]]")
        self.assertInvalid("metadata")

    def test_concept_alias_pipe_is_escaped_in_table(self):
        self.edit("hub.md", "#Distance]]", "#Distance\\|Distance]]")
        self.assertTrue(self.result()["ok"], self.result())

    def test_pdf_page_fragment(self):
        (self.package / "source.pdf").write_bytes(b"synthetic structural placeholder, not a PDF fidelity test")
        self.edit("hub.md", "## Resources", "## Resources\n\n[[source.pdf#page=1]]")
        self.assertTrue(self.result()["ok"], self.result())
        self.edit("hub.md", "#page=1", "#page=0")
        self.assertInvalid("anchor")

    def test_external_citation_not_fetched(self):
        self.edit("hub.md", "## Resources", "## Resources\n\n[Source](https://example.invalid/no-network)")
        self.assertTrue(self.result()["ok"], self.result())

    def test_noninteger_version(self):
        path = self.package / "course-package.json"
        data = json.loads(path.read_text())
        data["schema_version"] = True
        path.write_text(json.dumps(data))
        self.assertInvalid("schema")

    def test_yaml_duplicate_keys_rejected(self):
        self.edit("hub.md", "type: course", "type: course\ntype: course")
        self.assertInvalid("metadata")

    def test_json_duplicate_keys_rejected(self):
        path = self.package / "course-package.json"
        path.write_text(path.read_text().replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'))
        self.assertInvalid("read")

    def test_wrong_schema_types_report_without_traceback(self):
        path = self.package / "course-package.json"
        original = json.loads(path.read_text())
        for field in original:
            for value in (None, [], {}, True, 3.5):
                with self.subTest(field=field, value=value):
                    data = dict(original)
                    data[field] = value
                    path.write_text(json.dumps(data))
                    self.assertFalse(self.result()["ok"])

    def test_unicode_course_and_heading(self):
        self.package = make_course(self.root, course="Mécanique")
        self.edit("chapters/SYN - 01 - Motion.md", "## Distance", "## Déplacement")
        self.edit("hub.md", "#Distance]]", "#Déplacement]]")
        self.edit("Map.canvas", "#Distance", "#Déplacement")
        self.assertTrue(self.result()["ok"], self.result())

    def test_cli_failure_is_structured_nonzero(self):
        (self.package / "hub.md").unlink()
        result = subprocess.run([sys.executable, str(SCRIPT), "--package", str(self.package)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
