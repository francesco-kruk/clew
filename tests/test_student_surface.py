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

    def test_two_first_party_packages_share_one_immutable_revision(self):
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")
        references = re.findall(r"francesco-kruk/clew-skills/([^\s#]+)#([0-9a-f]{40})\b", manifest)
        self.assertEqual({path for path, _ in references},
                         {"skills/course-content", "skills/learner-model"})
        self.assertEqual(len(references), 2)
        self.assertEqual(len({revision for _, revision in references}), 1)
