# Advanced Skill Creator

Create, test, and distribute Claude skills. Five-minute drafts to fully evaluated, packaged skills with self-correcting quality loops.

**Activates when:** You want to build a skill from scratch, turn a workflow into something reusable, package and distribute a skill, or test whether a skill triggers reliably.

**Example usage:**

"Build me a skill for this workflow"
"Turn this into something reusable"
"I want a comprehensive skill with quality guardrails"
"Help me package and distribute this"

- 5 paths: Draft (5 min) · Draft+Test (15 min) · Full Eval (30 min) · Architect (1-2 hrs) · Package
- Architect path: generate, grade, extract patterns, iterate until quality stabilizes
- Rubric-based grading with explicit PASS/FAIL criteria per dimension
- Anti-pattern extraction from real failures, not invented rules
- Ships with `scripts/validate_skill.py` and `scripts/package_skill.py`

## Install

```bash
/plugin install advanced-skill-creator@cadence
```

Or manually:

```bash
git clone https://github.com/Cadence-Intelligence/skills.git
cd skills && ./install.sh advanced-skill-creator
```

## License

CC BY-NC 4.0, Cadence Intelligence, 2026
