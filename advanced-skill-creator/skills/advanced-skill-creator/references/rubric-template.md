# Quality Rubric Template

Use this as a starting point when designing rubrics for the Architect path. Adapt dimensions and weights to the specific skill being built.

## Format

```yaml
rubric:
  name: "[Skill Name] Quality Rubric"
  total_points: 100
  pass_threshold: 75

  dimensions:
    - name: "[Dimension Name]"
      weight: [points]
      grading: script | hybrid | judgment   # REQUIRED — see "Grading tags" below
      pass: "[Observable, binary criteria for PASS]"
      fail: "[Observable, binary criteria for FAIL]"
      evidence_required: "[What the grader must cite]"
      script_signals: |                      # optional; required if grading is script or hybrid
        [Concrete checks the script will run — regex, word count, schema validation]
```

## Grading tags (required on every dimension)

The `grading:` tag tells Phase 5 of the architect loop how to grade the
dimension. Every dimension must carry one of these three tags:

| Tag | Meaning | Examples |
|---|---|---|
| `script` | Fully mechanical: a regex, word count, list lookup, or schema check decides PASS/FAIL alone. No human or LLM judgment needed. | "No em dashes appear", "Output is valid JSON", "Word count between 600-1000" |
| `hybrid` | A script catches the obvious failures (cheap gate); judgment grades the rest. | "Length in band AND opener is a claim, not setup" — length is script, opener-quality is judgment |
| `judgment` | No mechanical shortcut. Must be read by a grader. If the criteria require user-specific taste (voice, brand, design), the **human** is the only valid grader (route to eval-viewer). Domain-neutral judgment can be LLM-graded. | "Sounds like the user's voice" (human only), "Heading hierarchy is logical" (LLM ok) |

**Routing implication:** if any `judgment` dimension is user-taste, the eval
round MUST end at the eval-viewer so the user grades it via `feedback.json`.
See SKILL.md "Who grades the output?" for the full routing rule.

## Universal Dimensions

Include these in every rubric (adjust weights):

### Information Completeness
```yaml
- name: "Information Completeness"
  weight: 20-30
  grading: hybrid
  pass: "All requested information is present. No sections missing, truncated, or containing placeholder text like TODO or TBD."
  fail: "One or more requested sections are missing, content is truncated mid-sentence, or placeholder text remains."
  evidence_required: "List every section/item from the input that should appear in the output. Check each one."
  script_signals: "Grep for TODO/TBD/placeholder. Check for sections listed in the input prompt."
```

### Anti-Pattern Free
```yaml
- name: "Anti-Pattern Free"
  weight: 15-25
  grading: script
  pass: "None of the anti-patterns listed in references/anti-patterns.md are present."
  fail: "One or more documented anti-patterns are present in the output."
  evidence_required: "Check each anti-pattern in the list. Cite any found with line/location."
  script_signals: "Each anti-pattern should be expressible as a regex or word-boundary match. Run them all and report hits."
```

## Domain-Specific Dimensions

Pick 2-4 from these based on skill type:

### For HTML / Visual Output Skills

```yaml
- name: "Aesthetic Distinctiveness"
  weight: 15-25
  pass: "Output would not be immediately identified as AI-generated. Uses a named font pairing (not Inter/Roboto/system-ui), a non-default color palette, and shows intentional layout asymmetry or hierarchy."
  fail: "Generic template appearance. Default fonts, Tailwind default colors, symmetric uniform layout, or any combination of Inter + violet/indigo accents."
  evidence_required: "Name the fonts used, the color palette, and the layout approach. Compare to common AI defaults."

- name: "Cross-Theme Support"
  weight: 10-15
  pass: "Both light and dark themes render correctly. Colors are defined as CSS custom properties with both variants. No text-on-text collisions in either theme."
  fail: "One theme is broken, missing, or clearly an afterthought. Hard-coded colors that only work in one theme."
  evidence_required: "Check :root and @media (prefers-color-scheme: dark). Verify contrast in both modes."

- name: "Responsive Layout"
  weight: 10-15
  pass: "Layout adapts gracefully from 400px to 1400px viewport width. No horizontal overflow. Grid collapses to single column on mobile. Text remains readable."
  fail: "Content clips or overflows at narrow widths. Layout breaks below 700px. Horizontal scrollbar appears."
  evidence_required: "Check for media queries, min-width: 0 on flex/grid children, overflow handling."
```

### For Document / Copy Skills

```yaml
- name: "Tone Consistency"
  weight: 15-20
  pass: "Voice and register are consistent throughout. Professional sections don't shift to casual. Technical sections don't shift to marketing speak."
  fail: "Tone shifts noticeably between sections. Inconsistent use of first/second/third person."
  evidence_required: "Quote 2-3 passages from different sections showing consistent (or inconsistent) voice."

- name: "Audience Fit"
  weight: 15-20
  pass: "Complexity level matches the target audience. Technical terms are explained when audience is non-technical. No over-simplification for expert audiences."
  fail: "Content is too technical for the stated audience, or too simplistic for experts."
  evidence_required: "Identify target audience and cite 2-3 passages that match (or mismatch) their level."

- name: "Structural Quality"
  weight: 15-20
  pass: "Clear heading hierarchy. Scannable sections. Logical progression from introduction to conclusion. Appropriate use of lists, tables, and callouts."
  fail: "Wall-of-text paragraphs. No clear section breaks. Random ordering of ideas."
  evidence_required: "Outline the document structure. Note any sections that seem misplaced or missing transitions."
```

### For Code Generation Skills

```yaml
- name: "Correctness"
  weight: 25-35
  pass: "Code runs without errors on the described input. Logic matches the stated requirements. Edge cases mentioned in the prompt are handled."
  fail: "Code has syntax errors, runtime errors, or produces wrong output for the stated use case."
  evidence_required: "Run the code (or trace it mentally). Cite specific inputs and expected vs actual outputs."

- name: "Idiom Compliance"
  weight: 15-20
  pass: "Code follows the conventions of its language/framework. Uses standard patterns, appropriate data structures, and community-standard naming."
  fail: "Code works but uses anti-patterns (e.g., Python code that reads like Java, React code that ignores hooks)."
  evidence_required: "Cite 2-3 examples of idiomatic (or non-idiomatic) patterns."
```

## Grading Process

For each output, grade every dimension using this structure:

```markdown
## Output N: [Description of input]

### [Dimension 1 Name] (weight: X)
<thinking>
[Reason through the evidence before committing to PASS/FAIL]
[Cite specific parts of the output]
[Compare to criteria]
</thinking>
**Verdict:** PASS/FAIL
**Score:** X/X
**Evidence:** [Specific citation from the output]

### [Dimension 2 Name] (weight: X)
...

### Summary
**Total Score:** X/100
**Key Strengths:** [What worked well]
**Key Failures:** [What needs fixing]
**Actionable Items:** [Specific things to add to anti-patterns or patterns]
```

## Weight Adjustment Rules

After Round 1, review whether the weights reflect reality:
- If the skill consistently passes a dimension easily → lower its weight (it's not differentiating)
- If the skill consistently fails a dimension → either raise its weight (it's important) or check if the criteria are too strict
- If two dimensions always pass/fail together → merge them or keep only the more specific one

## Example Rubrics

### For an HTML Diagram Skill (like cc-viz)
| Dimension | Weight |
|-----------|--------|
| Information Completeness | 25 |
| Aesthetic Distinctiveness | 25 |
| Anti-Pattern Free | 20 |
| Cross-Theme Support | 15 |
| Cross-Run Consistency | 15 |

### For a Blog Post Generator Skill
| Dimension | Weight |
|-----------|--------|
| Information Completeness | 25 |
| Tone Consistency | 20 |
| Audience Fit | 20 |
| Structural Quality | 20 |
| Anti-Pattern Free | 15 |

### For a CLI Wrapper Skill (simple — use Draft path instead)
Not recommended for Architect path. Use Draft + Test.
