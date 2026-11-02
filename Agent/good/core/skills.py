"""Discover Agent Skills and load their content on demand."""

from dataclasses import dataclass
from pathlib import Path
import re

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


def _validate_skill_content(name, content):
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("Skill 名称必须由小写字母、数字和单个连字符组成，且不能以连字符开头或结尾")
    if len(name) > 64:
        raise ValueError("Skill 名称不能超过 64 个字符")
    if not isinstance(content, str):
        raise ValueError("skillContext 必须是字符串")

    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md 必须以 YAML Frontmatter 分隔符 --- 开始")
    closing_line = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if closing_line is None:
        raise ValueError("SKILL.md 的 YAML Frontmatter 缺少结束分隔符 ---")
    try:
        metadata = YAML(typ="safe").load("".join(lines[1:closing_line]))
    except Exception as error:
        raise ValueError(f"SKILL.md 的 YAML Frontmatter 无效: {error}") from error
    if not isinstance(metadata, dict):
        raise ValueError("SKILL.md 的 YAML Frontmatter 必须是映射")
    if metadata.get("name") != name:
        raise ValueError(f"Frontmatter 中的 name 必须与工具参数一致: {name}")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Frontmatter 必须包含非空的 description")
    if len(description) > 1024:
        raise ValueError("Frontmatter 中的 description 不能超过 1024 个字符")
    if not "".join(lines[closing_line + 1 :]).strip():
        raise ValueError("SKILL.md 必须包含非空的正文内容")
    return description


def create_skill(name, content, project_root=None):
    """Create a validated Skill without replacing an existing directory."""
    description = _validate_skill_content(name, content)
    root = Path.cwd() if project_root is None else Path(project_root)
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    skill_dir = skills_dir / name
    try:
        skill_dir.mkdir()
    except FileExistsError:
        raise FileExistsError(f"目标 Skill 已存在，未覆盖: {skill_dir}")

    skill_path = skill_dir / "SKILL.md"
    try:
        with skill_path.open("x", encoding="utf-8") as skill_file:
            skill_file.write(content)
    except OSError:
        skill_dir.rmdir()
        raise
    return Skill(name, description, skill_path.resolve(), root.resolve())


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