#!/usr/bin/env python3
"""
Package a skill folder into a distributable .skill file (zip archive).

Usage:
    python3 scripts/package_skill.py <path/to/skill-folder> [output-directory]

Examples:
    python3 scripts/package_skill.py skills/my-skill
    python3 scripts/package_skill.py skills/my-skill ./dist
"""

import fnmatch
import sys
import zipfile
from pathlib import Path

# Make validate_skill importable when running from any working directory
sys.path.insert(0, str(Path(__file__).parent))
from validate_skill import validate_skill

EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}
# Excluded only at the skill root, not nested subdirectories
ROOT_EXCLUDE_DIRS = {"evals"}


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def package_skill(skill_path, output_dir=None):
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"Error: skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"Error: not a directory: {skill_path}")
        return None

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: SKILL.md not found in {skill_path}")
        return None

    print("Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"Validation failed:\n{message}")
        print("Fix validation errors before packaging.")
        return None
    print(f"{message}\n")

    output_path = Path(output_dir).resolve() if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)
    skill_filename = output_path / f"{skill_path.name}.skill"

    try:
        added = []
        skipped = []
        with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(skill_path.rglob("*")):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                if should_exclude(arcname):
                    skipped.append(str(arcname))
                    continue
                zf.write(file_path, arcname)
                added.append(str(arcname))

        for f in added:
            print(f"  + {f}")
        for f in skipped:
            print(f"  - {f} (excluded)")

        size = skill_filename.stat().st_size
        print(f"\nPackaged: {skill_filename} ({size:,} bytes, {len(added)} files)")
        return skill_filename

    except Exception as e:
        print(f"Error creating .skill file: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Packaging: {skill_path}")
    if output_dir:
        print(f"Output:    {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
