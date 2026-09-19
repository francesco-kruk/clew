"""Keep the student checkout independent of publishing and PDF tooling."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StudentSurfaceTests(unittest.TestCase):
    def test_only_vault_setup_is_local_runtime_code(self):
        files = {path.relative_to(ROOT / "src").as_posix()
                 for path in (ROOT / "src").rglob("*.py")}
        self.assertEqual(files, {"vault/__init__.py", "vault/cli.py", "vault/storage.py"})
        self.assertFalse((ROOT / "requirements.txt").exists())

    def test_pdf_skills_and_ingestion_agent_are_not_deployed(self):
        for name in ("content-ingest", "digest", "brute-force-pdf-to-obsidian"):
            with self.subTest(name=name):
                self.assertFalse((ROOT / ".agents" / "skills" / name / "SKILL.md").exists())
        self.assertFalse((ROOT / ".agents" / "agents" / "content-ingest.agent.md").exists())

    def test_three_first_party_packages_share_one_immutable_revision(self):
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")
        references = re.findall(r"francesco-kruk/clew-skills/([^\s#]+)#([0-9a-f]{40})\b", manifest)
        self.assertEqual({path for path, _ in references},
                         {"skills/teach", "skills/course-content", "skills/learner-model"})
        self.assertEqual(len(references), 3)
        self.assertEqual(len({revision for _, revision in references}), 1)

    def test_teaching_is_deployed_with_unchanged_reader_and_memory_versions(self):
        for name, version in (("teach", "1.0.0"), ("course-content", "2.0.0"),
                              ("learner-model", "3.0.0")):
            with self.subTest(name=name):
                package = ROOT / ".agents" / "skills" / name
                self.assertTrue((package / "SKILL.md").is_file())
                self.assertRegex((package / "apm.yml").read_text(encoding="utf-8"),
                                 rf"(?m)^version:\s*{re.escape(version)}\s*$")
        self.assertTrue((ROOT / ".agents" / "skills" / "teach" / "references"
                         / "static-visual.md").is_file())
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")
        self.assertRegex(manifest, r"(?m)^\s+- copilot\s*$")
        self.assertRegex(manifest, r"(?m)^\s+- agent-skills\s*$")

    def test_workspace_routes_tutoring_without_replacing_pure_lookup(self):
        for path in (ROOT / "AGENTS.md", ROOT / ".github" / "copilot-instructions.md"):
            with self.subTest(path=path):
                instructions = path.read_text(encoding="utf-8")
                self.assertIn("Load `teach` for active tutoring, attempted-work feedback, and retries",
                              instructions)
                self.assertIn("Pure source lookup uses `course-content`", instructions)
                self.assertIn("read-only `learner-model`", instructions)
                self.assertIn("Setup/path-only requests initialize no records", instructions)
                self.assertIn("no-save", instructions)
                self.assertIn("scoped stop-use", instructions)

    def test_installed_learner_contract_uses_compact_memory(self):
        package = ROOT / ".agents" / "skills" / "learner-model"
        self.assertRegex((package / "apm.yml").read_text(encoding="utf-8"),
                         r"(?m)^version:\s*3\.0\.0\s*$")
        references = package / "references"
        specification = (references / "learner-model-spec.md").read_text(encoding="utf-8")
        self.assertIn("<!-- clew-learning-memory: v1 -->", specification)
        self.assertIn("model/learner.md", specification)
        self.assertTrue((references / "clarification-gates.md").is_file())

    def test_archived_advanced_profiles_are_not_deployed(self):
        package = ROOT / ".agents" / "skills" / "learner-model"
        self.assertEqual(list(package.rglob("advanced*.md")), [])
        self.assertFalse((package / "docs" / "archive").exists())
