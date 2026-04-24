#!/usr/bin/env python3
"""
Validate a skill directory against the Agent Skills spec.

Usage:
    python3 scripts/validate_skill.py <skill_directory>

Exit codes: 0 = valid, 1 = invalid

Requires PyYAML (see scripts/requirements.txt).
"""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML is not installed.\n"
        "  pip install -r scripts/requirements.txt\n"
        "or: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)

# Claude Code built-in tools available to skills (as of Claude Code 2.x).
# MCP tools follow mcp__<server>__<tool>.
KNOWN_TOOLS = {
    "Agent", "Bash", "Edit", "Glob", "Grep", "LS", "MultiEdit",
    "NotebookEdit", "NotebookRead", "Read", "Skill", "SlashCommand",
    "TodoWrite", "WebFetch", "WebSearch", "Write",
}

# Agent Skills frontmatter spec. Slash-command-only fields
# (argument-hint, hooks, paths, shell, etc.) are intentionally excluded.
ALLOWED_FRONTMATTER_KEYS = {
    "name", "description", "license", "allowed-tools",
    "metadata", "compatibility",
}


def validate_skill(skill_path):
    """
    Validate a skill directory.

    Returns (valid: bool, message: str).
    Collects all issues instead of stopping at the first one.
    """
    skill_path = Path(skill_path)
    issues = []
    warnings = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return False, "No YAML frontmatter found (file must start with ---)"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter: missing closing ---"

    try:
        fm = yaml.safe_load(match.group(1))
        if not isinstance(fm, dict):
            return False, "Frontmatter must be a YAML mapping"
    except yaml.YAMLError as e:
        return False, f"YAML parse error in frontmatter: {e}"

    unexpected = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        issues.append(
            f"Unknown frontmatter key(s): {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}"
        )

    if "name" not in fm:
        issues.append("Missing required field: 'name'")
    if "description" not in fm:
        issues.append("Missing required field: 'description'")

    name = fm.get("name", "")
    if not isinstance(name, str):
        issues.append(f"'name' must be a string, got {type(name).__name__}")
    else:
        name = name.strip()
        if name:
            if not re.match(r"^[a-z0-9-]+$", name):
                issues.append(
                    f"Name '{name}' must be kebab-case (lowercase letters, digits, hyphens only)"
                )
            elif name.startswith("-") or name.endswith("-") or "--" in name:
                issues.append(
                    f"Name '{name}' cannot start/end with a hyphen or contain consecutive hyphens"
                )
            if len(name) > 64:
                issues.append(f"Name too long ({len(name)} chars, max 64)")

            if skill_path.name != name:
                issues.append(
                    f"Directory name '{skill_path.name}' does not match frontmatter name '{name}'"
                )

    desc = fm.get("description", "")
    if not isinstance(desc, str):
        issues.append(f"'description' must be a string, got {type(desc).__name__}")
    else:
        desc = desc.strip()
        if desc:
            if "<" in desc or ">" in desc:
                issues.append("Description cannot contain angle brackets (< or >)")
            if len(desc) > 1024:
                issues.append(f"Description too long ({len(desc)} chars, max 1024)")
            if len(desc) < 40:
                warnings.append(
                    f"Description is short ({len(desc)} chars) — "
                    "trigger reliability improves with concrete when-to-use phrasing"
                )

    compat = fm.get("compatibility", "")
    if compat and not isinstance(compat, str):
        issues.append(f"'compatibility' must be a string, got {type(compat).__name__}")
    elif compat and len(compat) > 500:
        issues.append(f"Compatibility too long ({len(compat)} chars, max 500)")

    allowed_tools = fm.get("allowed-tools")
    if allowed_tools is not None:
        if not isinstance(allowed_tools, str):
            issues.append("'allowed-tools' must be a string")
        else:
            tools = [t.strip() for t in allowed_tools.replace(",", " ").split() if t.strip()]
            unknown_tools = []
            mcp_tools = []
            for tool in tools:
                if tool.startswith("mcp__"):
                    parts = tool.split("__")
                    if len(parts) != 3 or not all(parts):
                        issues.append(
                            f"MCP tool '{tool}' must follow mcp__<server>__<tool> format"
                        )
                    else:
                        mcp_tools.append(tool)
                elif tool not in KNOWN_TOOLS:
                    unknown_tools.append(tool)
            if unknown_tools:
                issues.append(
                    f"Unknown tool(s) in allowed-tools: {', '.join(unknown_tools)}. "
                    f"Known tools: {', '.join(sorted(KNOWN_TOOLS))} (plus mcp__<server>__<tool>)"
                )
            if "Bash" in tools:
                warnings.append(
                    "Bash in allowed-tools grants shell access — confirm this is intentional"
                )
            for mcp_tool in mcp_tools:
                server = mcp_tool.split("__")[1]
                if server not in content:
                    warnings.append(
                        f"MCP server '{server}' declared in allowed-tools but not referenced in SKILL.md body"
                    )

    agents_dir = skill_path / "agents"
    if agents_dir.exists():
        for agent_file in agents_dir.iterdir():
            if agent_file.is_file() and agent_file.suffix != ".md":
                issues.append(
                    f"Agent file '{agent_file.name}' should be a .md file"
                )

    # Only check links that explicitly point into agents/
    agent_link_re = re.compile(r"\]\(agents/([^)\s]+\.md)\)")
    for ref in agent_link_re.findall(content):
        if not (skill_path / "agents" / ref).exists():
            warnings.append(f"Referenced agent file not found: agents/{ref}")

    if issues:
        lines = ["Validation failed:"] + [f"  - {i}" for i in issues]
        if warnings:
            lines += ["Warnings:"] + [f"  - {w}" for w in warnings]
        return False, "\n".join(lines)

    if warnings:
        lines = ["Skill is valid (with warnings):"] + [f"  - {w}" for w in warnings]
        return True, "\n".join(lines)

    return True, "Skill is valid"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_skill.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
