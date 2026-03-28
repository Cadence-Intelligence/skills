# JSON Schemas

Reference for all structured data formats used in the eval workflow.

---

## evals.json

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Human-readable description of success",
      "files": ["evals/files/sample.pdf"],
      "expectations": [
        "The output includes X",
        "The script used Y"
      ]
    }
  ]
}
```

---

## eval_metadata.json

Written per eval directory before runs start. Updated with assertions once drafted.

```json
{
  "eval_id": 1,
  "eval_name": "descriptive-name-here",
  "prompt": "The task prompt",
  "assertions": [
    "The output file is a valid PDF",
    "All required fields are present"
  ]
}
```

---

## timing.json

Captured from subagent task notification. Save immediately — not persisted elsewhere.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

---

## grading.json

Output from the grader agent. Field names must be exactly `text`, `passed`, `evidence`.

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. Output was a text file."
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2,
    "pass_rate": 0.5
  },
  "execution_metrics": {
    "tool_calls": {"Read": 5, "Write": 2, "Bash": 8},
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ]
}
```

---

## benchmark.json

Output from aggregate_benchmark script. Field names are read exactly by the viewer.

```json
{
  "metadata": {
    "skill_name": "my-skill",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "eval_name": "descriptive-name",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ]
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05},
      "time_seconds": {"mean": 45.0, "stddev": 12.0},
      "tokens": {"mean": 3800, "stddev": 400}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08},
      "time_seconds": {"mean": 32.0, "stddev": 8.0},
      "tokens": {"mean": 2100, "stddev": 300}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },
  "notes": [
    "Eval 3 shows high variance — may be flaky",
    "Without-skill runs consistently fail on table extraction"
  ]
}
```

**Important:** Use `"configuration": "with_skill"` or `"without_skill"` exactly.
The viewer groups and colors by these exact strings. Nest `pass_rate` under `result`,
not at the run's top level.

---

## comparison.json (blind comparator output)

```json
{
  "winner": "A",
  "reasoning": "Output A provides a complete solution...",
  "rubric": {
    "A": {
      "content": {"correctness": 5, "completeness": 5, "accuracy": 4},
      "structure": {"organization": 4, "formatting": 5, "usability": 4},
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {"correctness": 3, "completeness": 2, "accuracy": 3},
      "structure": {"organization": 3, "formatting": 2, "usability": 3},
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {"score": 9, "strengths": ["..."], "weaknesses": ["..."]},
    "B": {"score": 5, "strengths": ["..."], "weaknesses": ["..."]}
  }
}
```

---

## trigger-eval.json (description optimization)

```json
[
  {"query": "ok so my boss wants me to add a profit margin column to this xlsx...", "should_trigger": true},
  {"query": "write a python function that reads a csv and uploads rows to postgres", "should_trigger": false}
]
```
