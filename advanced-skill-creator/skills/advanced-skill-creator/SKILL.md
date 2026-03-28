---
name: advanced-skill-creator
description: >
  Create, test, and distribute Claude skills with a self-correcting Architect path.
  Use when the user wants to build a skill from scratch, turn a workflow into a
  reusable skill, edit or improve an existing SKILL.md, package a skill for
  distribution, test whether a skill works well, or optimize a skill's description
  so it triggers more reliably. Also use when the user asks how to make the agent
  remember a workflow, do something consistently in future sessions, or share a
  skill with others. For comprehensive, reference-heavy skills that produce creative
  or generative output (HTML, documents, designs, copy), use the Architect path.
license: CC BY-NC 4.0
metadata:
  author: cadence
  version: "1.0"
---

# Skill Creator

Create, test, and distribute skills — from a 5-minute draft to a fully
evaluated, packaged skill.

Works with both **pi** (Agent Skills standard) and **Claude Code** skill formats.

## Pick your path

| Path | When to use |
|------|-------------|
| **Draft only** | User wants a working SKILL.md fast, no testing |
| **Draft + test** | User wants to verify the skill works before using it |
| **Full eval** | User wants baseline comparisons, metrics, and description optimization |
| **Package existing** | User has a skill folder and just wants to distribute it |
| **Architect** | Deep skill with references, templates, anti-patterns, and self-correction loop. Use for skills that produce creative/generative output (HTML, documents, designs, copy) where quality varies across runs. |

When unsure, ask: *"Do you want a quick draft, or test and iterate?"*

**Auto-suggest Architect when:**
- The skill produces HTML, documents, copy, designs, or other creative output
- The user mentions "comprehensive", "high-quality", "like cc-viz", "detailed"
- The user wants anti-patterns, quality guardrails, or aesthetic guidelines
- Output quality would vary significantly across runs without guardrails

---

## Skill format reference

```
skill-name/              ← directory name must match frontmatter `name`
├── SKILL.md             ← required
├── scripts/             ← optional; executable code
├── references/          ← optional; docs loaded on demand
└── assets/              ← optional; templates, fonts, static files
```

### Frontmatter (required fields)

```yaml
---
name: kebab-case-name       # max 64 chars; [a-z0-9-] only; no leading/trailing hyphens
description: >              # max 1024 chars; this is the triggering mechanism
  What it does and when to use it.
license: MIT                # optional
compatibility: Requires...  # optional; max 500 chars
metadata:                   # optional; arbitrary key-value pairs
  author: example-org
  version: "1.0"
---
```

The `name` must match the parent directory name.

### Installation locations

| Scope | pi | Claude Code |
|-------|-----|-------------|
| Global | `~/.pi/agent/skills/` | `~/.claude/skills/` |
| Project | `.pi/skills/` | `.claude/skills/` (project-level) |
| Shared | `~/.agents/skills/` | `~/.agents/skills/` |

---

## Step 1 — Capture intent

Extract answers from the current conversation first — only ask what you can't infer:

- What should this skill help the agent do?
- When should it activate? (what user phrases or contexts)
- What does a good output look like?

If the user says "turn this into a skill," extract the workflow from the
conversation: tools used, step sequence, corrections made. Confirm before writing.

---

## Step 2 — Write the SKILL.md

### The description is the most important part

The description is the only thing the agent reads before deciding whether to load
the skill. Write it as an instruction, not a label. List concrete situations and
phrasings where the skill applies.

**Weak:** `"Helps with PDF files."`

**Strong:** `"Extract text, fill forms, and merge PDFs. Use when the user wants to
work with .pdf files, mentions forms or document extraction, or says things like
'read this file' or 'fill in this template.'"`

### Three-level loading

1. **Frontmatter** (~100 tokens): always in context for all skills
2. **SKILL.md body** (<500 lines / ~5k tokens): loads when skill activates
3. **Referenced files**: load on demand only when needed

Keep core workflow in SKILL.md. Move large reference material to `references/`.
Point to files clearly, including *when* to read them.

### Writing style

- Use imperative form: "Run the script" not "The script should be run"
- Explain the *why* behind instructions — agents follow reasoning better than commands
- Provide a clear default, then mention alternatives briefly
- For exact output formats, provide a template
- Add a **Gotchas** section for non-obvious facts the agent will get wrong without being told

### Calibrating specificity

Match prescription level to task fragility:

- **High freedom**: multiple valid approaches → explain the goal, let agent decide
- **Medium freedom**: preferred pattern exists → pseudocode or parameterized script
- **Low freedom**: fragile operation, consistency critical → exact script, few params

### Common patterns

**Sequential checklist** (helps agent track progress):
```markdown
- [ ] Step 1: Analyze the form (`scripts/analyze_form.py`)
- [ ] Step 2: Create field mapping (edit `fields.json`)
- [ ] Step 3: Validate (`scripts/validate.py`) — fix errors, re-validate until clean
```

**Validation loop** (agent self-corrects):
```markdown
1. Do the work
2. Run `scripts/validate.py output/`
3. If it fails, fix the issues and re-run. Only proceed when it passes.
```

**Variant dispatch** (loads only what's needed):
```markdown
Read the relevant reference before proceeding:
- AWS → `references/aws.md`
- GCP → `references/gcp.md`
```

### Scripts in `scripts/`

Design for agentic use:
- No interactive prompts — accept all input via flags, env vars, or stdin
- `--help` flag with usage examples
- Clear error messages
- Structured output (JSON/CSV) to stdout; diagnostics to stderr
- Idempotent where possible — agents may retry

---

## Step 3 — Test the skill (optional but recommended)

After drafting, propose 2–3 test prompts. Share them: *"Here are a few test cases
— do these look right?"* Then run them.

### Running tests in pi

For each test prompt, run two parallel pi instances via bash:

**With-skill run:**
```bash
pi -p --skill <path-to-skill-folder> "<test prompt>" \
  > <workspace>/with_skill/output.md 2>&1 &
```

**Baseline run** (same prompt, no skill):
```bash
pi -p --no-skills "<test prompt>" \
  > <workspace>/without_skill/output.md 2>&1 &
wait
```

If parallel runs aren't practical, run sequentially — with-skill first, then baseline.

### Reviewing and iterating

Present with-skill and baseline outputs side by side. Ask: *"How does this look?
Anything you'd change?"*

When improving based on feedback:
- Generalize — the skill will run many times on varied prompts
- Trim instructions that aren't helping; lean prompts often outperform verbose ones
- If every test run reinvented the same helper script, bundle it in `scripts/`

### Grading (for full eval path)

Read [agents/grader.md](agents/grader.md) for the grading methodology. Follow the
grader instructions yourself to evaluate each test run:

1. Define expectations (what should the output contain/accomplish?)
2. Read the output
3. Grade each expectation as PASS/FAIL with evidence
4. Critique the evals themselves (are the assertions strong enough?)
5. Save results as `grading.json`

### Blind comparison (for full eval path)

Read [agents/comparator.md](agents/comparator.md) for blind A/B comparison methodology:

1. Label outputs as A and B (randomize which is skill vs baseline)
2. Judge purely on quality without knowing which is which
3. Pick a winner with reasoning
4. Unblind and analyze using [agents/analyzer.md](agents/analyzer.md)

For full quantitative benchmarking details:
→ see [references/advanced-eval.md](references/advanced-eval.md)

---

## Step 4 — Package for distribution

### As a pi package (npm)

If the skill should be installable via `pi install`:

```json
{
  "name": "my-skill-package",
  "keywords": ["pi-package"],
  "pi": {
    "skills": ["./skills"]
  }
}
```

### As a .skill file (zip archive)

Use the bundled packager. It validates first, then zips, excluding `evals/`,
`__pycache__`, `.DS_Store`, and `node_modules`:

```bash
python3 scripts/package_skill.py path/to/my-skill
python3 scripts/package_skill.py path/to/my-skill ./dist   # custom output dir
```

See [scripts/package_skill.py](scripts/package_skill.py) for the full implementation.

### Installing a .skill file

```bash
# Extract and place in skills directory
unzip my-skill.skill -d ~/.pi/agent/skills/
# Or for Claude Code:
unzip my-skill.skill -d ~/.claude/skills/
```

### Validate before packaging

Run the validator directly to check a skill without packaging:

```bash
python3 scripts/validate_skill.py path/to/my-skill
```

See [scripts/validate_skill.py](scripts/validate_skill.py) for the full implementation.

Checks performed:
- `name` is kebab-case, max 64 chars, matches directory name
- `description` has no angle brackets, max 1024 chars
- `compatibility` max 500 chars
- No unexpected frontmatter keys
- `allowed-tools` — validates against known Claude tools; MCP tools must follow `mcp__<server>__<tool>` format; warns if Bash is included; warns if a declared MCP server isn't referenced in the skill body
- `agents/` directory — all files must be `.md`; referenced agent files must exist

---

## Step 5 — Optimize the description (advanced)

If the skill isn't triggering when it should:

1. Write 10–15 test phrases (mix of should/shouldn't trigger)
2. Include near-misses — phrases that share keywords but need something different
3. Run them via `pi -p` and note whether the skill was loaded
4. Revise the description to address the pattern, not specific query wording
5. Repeat until stable

### Trigger eval format

```json
[
  {"query": "ok so my boss wants me to add a profit margin column to this xlsx...", "should_trigger": true},
  {"query": "write a python function that reads a csv and uploads each row to postgres", "should_trigger": false}
]
```

Good should-not-trigger queries are near-misses, not obviously irrelevant ones.

For the full optimization workflow: → [references/advanced-eval.md](references/advanced-eval.md)

---

## Architect Path — Self-Correcting Skill Builder

For skills that produce creative or generative output where quality matters and varies across runs. Read [references/architect-workflow.md](references/architect-workflow.md) for the full detailed workflow before starting.

The architect path builds skills through a **generate → grade → extract → iterate** loop that produces reference-heavy skills with anti-patterns, templates, and quality guardrails — similar to how cc-viz was built.

### Overview: The Loop

```
Phase 1: Capture intent + style examples + anti-examples
Phase 2: Design quality rubric (BEFORE writing any skill code)
Phase 3: Write draft SKILL.md (intentionally minimal)
Phase 4: Generate 3-4 real outputs on varied inputs
Phase 5: Grade each output against rubric
Phase 6: Extract patterns (from successes) + anti-patterns (from failures)
Phase 7: Create reference templates from best outputs
Phase 8: Update SKILL.md with lessons learned
Phase 9: Repeat Phases 4-8 until quality stabilizes (2-3 rounds)
Phase 10: Polish and package
```

### Phase 1 — Capture Intent (Extended)

Same as Step 1, plus these architect-specific questions:

- **Style examples:** "Show me 2-3 examples of what good output looks like" (URLs, files, screenshots)
- **Anti-examples:** "What should it NOT look like?" (generic AI output, specific bad patterns)
- **Quality dimensions:** What matters most? (accuracy, aesthetics, consistency, completeness, distinctiveness)
- **Audience:** Who sees the output? (developer, PM, client, public)

### Phase 2 — Design the Quality Rubric

**Do this BEFORE writing any skill code.** The rubric is the foundation the entire loop grades against.

Read [references/rubric-template.md](references/rubric-template.md) for the default format and adapt it to the specific skill.

A rubric has 4-6 weighted dimensions, each with explicit PASS/FAIL criteria:

```yaml
dimensions:
  - name: "Information Completeness"
    weight: 25
    pass: "All requested information present. Nothing missing or truncated."
    fail: "Missing sections, placeholder text, or incomplete content."

  - name: "Structural Quality"
    weight: 20
    pass: "Clear hierarchy, logical flow, appropriate sections."
    fail: "Flat structure, no visual hierarchy, walls of text."

  - name: "Distinctiveness"
    weight: 20
    pass: "Would not be immediately identified as AI-generated."
    fail: "Generic template feel. Default fonts/colors. No design intent."

  - name: "Anti-Pattern Free"
    weight: 20
    pass: "None of the documented anti-patterns are present."
    fail: "Contains one or more known anti-patterns."

  - name: "Cross-Run Consistency"
    weight: 15
    pass: "Quality is similar across different inputs."
    fail: "Great on some inputs, terrible on others."
```

Save the rubric to `references/quality-rubric.md` in the skill folder.

### Phase 3 — Draft SKILL.md (V1)

Write a minimal first version:
- Core workflow (what the skill does step by step)
- Basic quality guidelines
- **No references or templates yet** — those come from the loop

This is intentionally sparse. The references will be extracted from real outputs, not invented upfront.

### Phase 4 — Generate Round

Run the draft skill on 3-4 **deliberately varied** inputs:

| Input | Purpose |
|-------|---------|
| Typical/common case | Does it handle the bread-and-butter? |
| Complex/large case | Does it scale? Does quality degrade? |
| Edge case / unusual | Does it handle ambiguity gracefully? |
| Minimal input | What does it do with almost no guidance? |

Save all outputs to a workspace folder: `evals/round-N/output-1.ext`, etc.

**Speed option:** Delegate generation to other agents via `interactive_shell` dispatch or `coding_task` for parallel runs. Keep Round 1 in-session (need the context), Rounds 2-3 can be delegated.

### Phase 5 — Grade

For each output, grade against every rubric dimension using `<thinking>` to reason before scoring:

```xml
<thinking>
Checking "Distinctiveness" for output-1:
- Font: Uses DM Sans + Fira Code — good, not a default
- Color: Terracotta/sage palette — distinctive, earthy
- Layout: Asymmetric grid with varied card depths — shows intent
- Would I think "AI generated this"? No — the palette and asymmetry are unusual
→ PASS
</thinking>
```

Produce a structured grade card per output:

```
Output 1 (typical case): 82/100
  ✅ Information Completeness (25/25)
  ✅ Structural Quality (20/20)
  ✅ Distinctiveness (20/20)
  ❌ Anti-Pattern Free (10/20) — emoji in section headers
  ✅ Cross-Run Consistency (7/15) — first run, limited data
```

Save to `evals/round-N-grades.md`.

### Phase 6 — Extract Patterns

From the grades, extract two things:

**Anti-patterns (from failures):**
```markdown
### Anti-Pattern: [Name]
**What happens:** [Describe the bad output]
**Why it's bad:** [Why this signals low quality]
**Rule:** [The explicit prohibition]
**Instead:** [What to do instead, with example]
```

**Winning patterns (from successes):**
```markdown
### Pattern: [Name]
**What it does:** [Describe the technique]
**When to use:** [Context where this works]
**Example:** [Code/markup snippet]
```

Append to `references/anti-patterns.md` and `references/patterns.md`.

### Phase 7 — Create Reference Templates

Take the highest-scoring output and save it as a reference template.

**Critical rule: Templates MUST be deliberately varied.**
- If Round 1 template is dark with teal accents → Round 2 must be light with warm tones
- If Round 1 template uses Mermaid diagrams → Round 2 should use CSS Grid
- If Round 1 template is minimal → Round 2 should be information-dense

Add a comment header to each template:
```html
<!--
  Reference template: [name]
  Aesthetic: [description]
  Palette: [colors]
  Patterns used: [list from references/patterns.md]
  Deliberately different from: [other template name]
-->
```

### Phase 8 — Update SKILL.md

Based on what grading revealed:
- Add "Read the reference template before generating" instructions
- Add anti-pattern rules (summary in SKILL.md, details in references/)
- Add quality checks section
- Refine workflow with lessons learned
- Add "Read `references/anti-patterns.md` before every generation" instruction

### Phase 9 — Iterate

Repeat Phases 4-8 with the updated skill on **new inputs** (not the same ones).

**Convergence criteria (stop when ALL met):**
- Average score ≥ 75/100 across all outputs in the round
- No FAIL on any dimension in 2+ consecutive outputs
- Anti-pattern list has stabilized (no new patterns in last round)
- At least 2 varied reference templates exist

Typically 2-3 rounds. If scores aren't improving after 3 rounds, revisit the rubric — dimensions may need adjustment.

### Phase 10 — Polish & Package

Final deliverable structure:
```
skill-name/
├── SKILL.md                    ← Workflow + quality checks + anti-pattern summary
├── README.md                   ← Architecture, for maintainers
├── references/
│   ├── quality-rubric.md       ← Grading criteria
│   ├── patterns.md             ← Winning patterns with examples
│   ├── anti-patterns.md        ← Failure patterns with rules
│   └── [domain-specific].md    ← E.g., css-patterns.md, api-reference.md
├── templates/
│   ├── template-1.ext          ← Best from Round 1 (with style comment)
│   └── template-2.ext          ← Best from Round 2 (deliberately different)
└── evals/                      ← Optional: grading history for re-evaluation
    ├── round-1-grades.md
    └── round-2-grades.md
```

Run Step 4 (Package) and Step 5 (Description Optimization) from the standard paths.

---

## Reference files

Read these only when the user explicitly wants the advanced path:

- [references/advanced-eval.md](references/advanced-eval.md) — Quantitative grading, benchmark viewer, blind A/B comparison
- [references/schemas.md](references/schemas.md) — JSON schemas for evals.json, grading.json, benchmark.json
- [references/architect-workflow.md](references/architect-workflow.md) — Detailed architect path workflow with prompt engineering principles
- [references/rubric-template.md](references/rubric-template.md) — Default quality rubric format and examples
- [agents/grader.md](agents/grader.md) — Instructions for evaluating assertions against outputs
- [agents/comparator.md](agents/comparator.md) — Instructions for blind A/B comparison
- [agents/analyzer.md](agents/analyzer.md) — Instructions for post-hoc "why did the winner win" analysis
