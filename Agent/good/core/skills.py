"""Discover Agent Skills and load their content on demand."""

from dataclasses import dataclass
from pathlib import Path

from ruamel.yaml import YAML


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    path: Path
    project_root: Path

    def load(self):
        return self.path.read_text(encoding="utf-8")

    def load_file(self, filename=None):
        if filename is None:
            return self.load()
        if not isinstance(filename, str):
            return "错误：filename 必须是字符串"
        if not filename.strip():
            return "错误：filename 不能为空字符串"

        requested = Path(filename)
        if requested.is_absolute():
            candidates = [requested]
        else:
            candidates = [self.path.parent / requested, self.project_root / requested]

        skill_dir = self.path.parent.resolve()
        resolved_candidates = []
        outside_skill = False
        for candidate in candidates:
            try:
                resolved = candidate.resolve(strict=True)
            except (OSError, RuntimeError):
                continue
            if not resolved.is_relative_to(skill_dir):
                outside_skill = True
                continue
            if resolved.is_file() and resolved not in resolved_candidates:
                resolved_candidates.append(resolved)

        if len(resolved_candidates) == 1:
            return _read_text(resolved_candidates[0])
        if len(resolved_candidates) > 1:
            return _ambiguous_files(resolved_candidates, skill_dir)

        if requested.parent == Path("."):
            matches = sorted(
                path.resolve()
                for path in self.path.parent.rglob(requested.name)
                if path.is_file() and path.resolve().is_relative_to(skill_dir)
            )
            if len(matches) == 1:
                return _read_text(matches[0])
            if len(matches) > 1:
                return _ambiguous_files(matches, skill_dir)

        if outside_skill:
            return "错误：只能读取指定 Skill 目录内的文件"
        return f"错误：Skill 文件不存在: {filename}"


def _read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return f"错误：无法读取 Skill 文件: {error}"


def _ambiguous_files(paths, skill_dir):
    candidates = "\n".join(f"- {path.relative_to(skill_dir).as_posix()}" for path in paths)
    return f"找到多个匹配文件，请用相对路径指定其中一个：\n{candidates}"


def _read_frontmatter(path):
    lines = []
    with path.open(encoding="utf-8") as skill_file:
        if skill_file.readline().strip() != "---":
            raise ValueError(f"Skill frontmatter must start with ---: {path}")
        for line in skill_file:
            if line.strip() == "---":
                metadata = YAML(typ="safe").load("".join(lines))
                if not isinstance(metadata, dict):
                    raise ValueError(f"Skill frontmatter must be a YAML mapping: {path}")
                return metadata
            lines.append(line)
    raise ValueError(f"Skill frontmatter is not closed: {path}")


def discover_skills(project_root=None):
    """Return skill metadata indexed by name, without reading skill bodies."""
    root = Path.cwd() if project_root is None else Path(project_root)
    skills_dir = root / ".agents" / "skills"
    if not skills_dir.is_dir():
        return {}

    skills = {}
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_path = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_path.is_file():
            continue

        metadata = _read_frontmatter(skill_path)
        name = metadata.get("name")
        description = metadata.get("description")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Skill is missing a non-empty name: {skill_path}")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"Skill is missing a non-empty description: {skill_path}")
        if name in skills:
            raise ValueError(f"Duplicate Skill name '{name}': {skill_path}")
        skills[name] = Skill(name, description, skill_path.resolve(), root.resolve())

    return skills