import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.skills import discover_skills
from core.agent import Agent
from core.tools import run_tool, tools


class DiscoverSkillsTests(unittest.TestCase):
    def create_skill(self, root):
        skill_dir = Path(root) / ".agents" / "skills" / "demo"
        skill_dir.mkdir(parents=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(
            "---\n"
            "name: demo\n"
            "description: >-\n"
            "  Demo description\n"
            "---\n"
            "Skill body\n",
            encoding="utf-8",
        )
        return skill_dir, skill_path

    def test_discovers_metadata_and_loads_body_on_demand(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            _, skill_path = self.create_skill(temp_dir)

            skills = discover_skills(temp_dir)

            self.assertEqual(list(skills), ["demo"])
            self.assertEqual(skills["demo"].description, "Demo description")
            self.assertEqual(skills["demo"].load(), skill_path.read_text(encoding="utf-8"))
            self.assertIn("不能为空", skills["demo"].load_file(""))
            self.assertIn(
                "loadSkill",
                [tool["function"]["name"] for tool in tools],
            )
            self.assertEqual(
                run_tool("loadSkill", json.dumps({"name": "demo"}), skills=skills),
                skill_path.read_text(encoding="utf-8"),
            )

    def test_injects_skill_metadata_into_system_prompt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.create_skill(temp_dir)
            previous_cwd = Path.cwd()
            os.chdir(temp_dir)
            try:
                agent = Agent("url", "key", "model")
            finally:
                os.chdir(previous_cwd)

            system_message = agent.messages[0]
            self.assertEqual(system_message["role"], "system")
            self.assertIn("`demo`: Demo description", system_message["content"])
            self.assertIn("`loadSkill`", system_message["content"])

    def test_loads_skill_files_by_supported_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir, _ = self.create_skill(temp_dir)
            references = skill_dir / "references"
            references.mkdir()
            relative_file = references / "relative.md"
            relative_file.write_text("relative", encoding="utf-8")
            project_file = references / "project.md"
            project_file.write_text("project", encoding="utf-8")
            absolute_file = references / "absolute.md"
            absolute_file.write_text("absolute", encoding="utf-8")
            unique_file = references / "unique.md"
            unique_file.write_text("unique", encoding="utf-8")
            nested_file = references / "nested-only.md"
            nested_file.write_text("nested", encoding="utf-8")
            (Path(temp_dir) / "nested-only.md").write_text("outside", encoding="utf-8")

            skill = discover_skills(temp_dir)["demo"]

            self.assertEqual(skill.load_file("references/relative.md"), "relative")
            self.assertEqual(
                skill.load_file(".agents/skills/demo/references/project.md"), "project"
            )
            self.assertEqual(skill.load_file(str(absolute_file)), "absolute")
            self.assertEqual(skill.load_file("unique.md"), "unique")
            self.assertEqual(skill.load_file("nested-only.md"), "nested")

    def test_ambiguous_filename_returns_candidates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir, _ = self.create_skill(temp_dir)
            for directory in ("one", "two"):
                match_dir = skill_dir / directory
                match_dir.mkdir()
                (match_dir / "guide.md").write_text(directory, encoding="utf-8")

            result = discover_skills(temp_dir)["demo"].load_file("guide.md")

            self.assertIn("one/guide.md", result)
            self.assertIn("two/guide.md", result)

    def test_rejects_paths_outside_skill_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir, _ = self.create_skill(temp_dir)
            outside_file = Path(temp_dir) / "outside.txt"
            outside_file.write_text("must not be read", encoding="utf-8")
            skill = discover_skills(temp_dir)["demo"]

            self.assertIn("只能读取指定 Skill 目录内", skill.load_file("../../../outside.txt"))
            self.assertIn("只能读取指定 Skill 目录内", skill.load_file(str(outside_file)))

    def test_returns_empty_registry_when_skills_directory_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(discover_skills(temp_dir), {})


if __name__ == "__main__":
    unittest.main()