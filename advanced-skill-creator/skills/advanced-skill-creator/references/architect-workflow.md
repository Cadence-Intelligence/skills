# Architect Workflow — Detailed Reference

This document provides the full detailed workflow for the Architect path. The SKILL.md has the overview — read this for implementation details, prompt engineering principles, and worked examples.

## Core Principle: Build From Outputs, Not Imagination

The biggest mistake in building a generative skill is writing all the rules upfront and hoping they work. The architect path does the opposite:

1. Write a minimal draft
2. See what the AI actually produces
3. Grade it honestly
4. Extract what worked and what didn't
5. Feed those lessons back into the skill
6. Repeat until stable

The references and anti-patterns emerge from reality, not theory. This is why cc-viz works — every rule in that skill was learned from a real failure.

## Prompt Engineering Principles

These principles (from Anthropic's best practices) are embedded throughout the architect workflow:

### 1. Self-Correction Chain
The generate → grade → refine loop is an explicit self-correction chain. Each step produces structured output the next step can act on. Don't let the agent "just try again" — make it grade, identify specific failures, and fix those specific things.

### 2. XML-Tagged Structure
Use XML tags in SKILL.md to separate concerns:
```xml
<workflow>Step-by-step instructions</workflow>
<anti-patterns>What NOT to do</anti-patterns>
<quality-checks>Verification before delivery</quality-checks>
```
This helps the agent parse complex skills unambiguously, especially when mixing instructions, examples, and reference material.

### 3. Few-Shot with Good AND Bad Examples
Reference templates are "good" examples. Anti-patterns are "bad" examples with explicit "instead, do this" alternatives. Both are necessary:
- Good examples alone → agent copies them too closely, no variety
- Bad examples alone → agent knows what to avoid but not what to aim for
- Both together → agent navigates toward quality while avoiding traps

### 4. Rubric-Based Grading
Every dimension has explicit PASS/FAIL criteria with evidence. This prevents vibes-based grading where "it looks fine" lets mediocre output through. The rubric forces the grader to check specific things.

### 5. Extended Thinking for Grading
When grading, use `<thinking>` tags to reason about each dimension before scoring. This produces better grades because the agent reasons through the evidence before committing to PASS/FAIL.

### 6. Diversity Through Constraint
Templates use deliberately different aesthetics/approaches. The instruction "read the template before generating" forces the agent to absorb a specific style each time, preventing default convergence. Without this, every generation drifts toward the same generic output.

### 7. Anti-Patterns Over Positive Rules
"Don't use Inter font" is more actionable than "use good typography." Negative examples are stronger signals for LLMs because they create bright-line rules the agent can check mechanically. Positive rules ("use distinctive fonts") leave too much room for interpretation.

## Rubric Design Guidelines

### Choosing Dimensions

A good rubric has 4-6 dimensions. More than 6 creates grading fatigue. Fewer than 4 misses important quality signals.

**Universal dimensions** (include in most rubrics):
- Information Completeness — Is everything the user asked for actually present?
- Anti-Pattern Free — Does the output avoid known failure patterns?

**Domain-specific dimensions** (pick 2-4 based on the skill):

| Skill type | Relevant dimensions |
|-----------|-------------------|
| HTML/visual output | Aesthetic Distinctiveness, Cross-Theme Support, Responsive Layout |
| Document/copy | Tone Consistency, Audience Fit, Structure Quality |
| Code generation | Correctness, Idiom Compliance, Error Handling |
| Data processing | Accuracy, Completeness, Edge Case Handling |

### Weight Distribution

Weights should reflect what actually matters for the skill's purpose:
- If the skill exists to prevent generic AI output → weight Distinctiveness highest
- If the skill processes critical data → weight Accuracy highest
- If the skill must work across many inputs → weight Consistency highest

Total weights should sum to 100 for easy scoring.

### Writing PASS/FAIL Criteria

Good criteria are:
- **Observable** — can be checked by reading the output, not by guessing intent
- **Binary** — either the output has it or it doesn't (no "mostly" or "somewhat")
- **Specific** — "Uses a non-default font pairing" not "Has good typography"
- **Evidence-based** — the grader must cite what they see, not what they feel

Bad criteria: "The output feels professional" (not observable, not binary)
Good criteria: "The output uses a named font pairing from the approved list, not Inter/Roboto/system-ui" (observable, binary, specific)

## Pattern Extraction Guidelines

### Extracting Anti-Patterns

When an output fails a rubric dimension, ask:
1. What specifically is wrong? (Not "it looks generic" but "it uses Inter font with violet-500 accents")
2. Why does the agent do this? (Default behavior, training data bias, lazy path)
3. What's the bright-line rule? (Never use X, always check Y before Z)
4. What should replace it? (Concrete alternative with example)

**Format:**
```markdown
### Anti-Pattern: [Descriptive Name]
**What happens:** Agent does [specific bad thing]
**Why:** [Root cause — default behavior, ambiguous instruction, etc.]
**Rule:** Never [specific prohibition]
**Instead:** [Concrete alternative]
**Example of bad output:**
[Snippet showing the anti-pattern]
**Example of good output:**
[Snippet showing the fix]
```

### Extracting Winning Patterns

When an output scores well on a dimension, ask:
1. What specific technique made this work?
2. Is it reusable across different inputs?
3. Can I extract it as a snippet/template other generations can reference?

**Format:**
```markdown
### Pattern: [Descriptive Name]
**What:** [The technique]
**When:** [Context where it applies]
**Why it works:** [What quality signal it produces]
**Example:**
[Reusable snippet]
```

## Template Variance Enforcement

The biggest risk with reference templates is convergence — every output starts looking the same because the agent copies the template too closely.

**Rules for template variance:**
1. Each template MUST use a different font pairing
2. Each template MUST use a different color palette
3. Each template MUST use a different layout approach (grid, flex, single-column, sidebar)
4. Each template MUST target a different aesthetic direction
5. Add a comment header to each template naming what it's different from

**The variance check:** Before saving a new template, compare it to existing ones. If you could swap the content between templates and nobody would notice a visual difference, the new template isn't varied enough.

## Convergence Criteria

Stop iterating when ALL of these are met:
- Average score ≥ 75/100 across all outputs in the latest round
- No dimension scores FAIL in 2+ consecutive outputs
- Anti-pattern list has stabilized (no new patterns discovered in the last round)
- At least 2 varied reference templates exist
- The user is satisfied with sample output quality

**If scores plateau below 75 after 3 rounds:**
- Revisit the rubric — dimensions might be too strict or misaligned
- Check if the skill's task is too broad — split into sub-skills
- Check if the anti-patterns are contradicting each other
- Consider whether the quality ceiling is lower than expected for this type of output

## Delegation Strategy

For speed, generation rounds can be delegated:

| Round | Approach | Why |
|-------|----------|-----|
| Round 1 | In-session | Need full conversation context for first draft |
| Round 2+ | Delegate via `interactive_shell` dispatch or `coding_task` | Faster, parallel, and tests whether the skill works without conversation context |

Delegated agents should receive:
- The skill folder (SKILL.md + references + templates)
- The test input
- Instructions to generate output following the skill
- No additional context (this tests whether the skill is self-contained)

## Worked Example: Building a Report Generator Skill

**Phase 1 — Intent:**
"I want a skill that generates weekly project status reports as styled HTML pages."

**Phase 2 — Rubric:**
- Information Completeness (30): All project metrics, risks, and milestones present
- Visual Clarity (25): Scannable in under 30 seconds by a PM
- Aesthetic Quality (20): Professional, not generic
- Anti-Pattern Free (15): No known bad patterns
- Consistency (10): Similar quality across different project types

**Phase 3 — Draft V1:** Basic SKILL.md with "generate an HTML report with project status."

**Phase 4 — Round 1 (3 outputs):**
- Output 1 (web project): Score 55. Used Inter font, flat card grid, no hierarchy.
- Output 2 (mobile project): Score 62. Better layout, but emoji in headers, gradient text.
- Output 3 (data pipeline): Score 48. Missing risk section entirely. Generic dark theme.

**Phase 5 — Extracted anti-patterns:**
- Default typography (Inter/Roboto)
- Emoji section headers
- Gradient text on headings
- Missing sections when input doesn't mention them explicitly

**Phase 6 — Extracted patterns:**
- KPI cards with trend indicators (from Output 2's metrics section)
- Risk matrix color coding (invented for Output 3 fix)

**Phase 7 — Template 1:** Best parts of Output 2, fixed anti-patterns. IBM Plex Sans + warm palette.

**Phase 8 — Updated SKILL.md:** Added "read template before generating", anti-pattern list, "always include Risk section even if input doesn't mention risks."

**Round 2 (3 new outputs):** Average score 78. One FAIL on consistency (Output 3 was info-dense but visually cluttered). Added pattern for "information density scaling" to references.

**Round 3 (2 outputs):** Average score 84. No FAILs. New template with dark editorial aesthetic. Skill complete.
