#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes Claude to trigger (load/use the
skill) for a set of queries. Outputs results as JSON.

Methodology:
  For each query, spawn an isolated `claude -p` with a project-local probe
  skill carrying the candidate description. Capture the full assistant
  response, then run a second `claude -p` as an LLM judge that classifies
  TRIGGERED vs NOT_TRIGGERED based on whether the response relied on the
  skill.

  This replaces a stream-event detection scheme that watched for `Skill`
  tool calls — that approach was unreliable on Claude Code 2.x, where
  skills often fire passively from the system prompt without emitting a
  `Skill` tool event.

Uses Claude Code subscription auth — no ANTHROPIC_API_KEY required.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import parse_skill_md


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .claude/."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def _call_claude(
    prompt: str,
    cwd: str,
    timeout: int,
    model: str | None = None,
) -> str:
    """Run `claude -p <prompt>` and return the final assistant text."""
    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return ""
    except FileNotFoundError:
        raise SystemExit("Error: `claude` CLI not found on PATH.")

    if result.returncode != 0:
        return ""
    return result.stdout.strip()


JUDGE_PROMPT_TEMPLATE = """You are judging whether a Claude Code skill was triggered and relied on by an assistant response.

A "skill" is a named prompt-like resource. When Claude deems a skill relevant to the user's query, it uses the skill's guidance to answer. The question is NOT whether the response mentions the skill by name — it's whether the response *behaved as if* this particular skill was loaded and followed.

## Skill under test
Name: {skill_name}
Description: {skill_description}

## The user's query
{query}

## The assistant's response to that query
{response}

## Your job
Decide if the response's content, structure, or approach reflects the skill's description — did it follow the guidance that description implies, ask the kinds of questions that description implies, or produce the kind of output that description implies?

- If YES (the response clearly reflects the skill's guidance): answer TRIGGERED
- If NO (the response is generic, or reflects a different skill/approach, or doesn't engage with the skill's domain): answer NOT_TRIGGERED
- If AMBIGUOUS: answer NOT_TRIGGERED (be strict — only clear triggers count).

Respond with exactly one of: TRIGGERED or NOT_TRIGGERED. No explanation."""


def _judge_response(
    skill_name: str,
    skill_description: str,
    query: str,
    response: str,
    judge_cwd: str,
    timeout: int,
    model: str | None,
) -> bool:
    """Ask a fresh claude -p to classify whether the response triggered the skill."""
    if not response:
        return False
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        skill_name=skill_name,
        skill_description=skill_description.strip(),
        query=query,
        response=response[:6000],  # cap so we don't blow the judge's context
    )
    verdict = _call_claude(prompt, cwd=judge_cwd, timeout=timeout, model=model).upper()
    return "TRIGGERED" in verdict and "NOT_TRIGGERED" not in verdict


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    judge_timeout: int,
    project_root: str,
    model: str | None = None,
    judge_model: str | None = None,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    1. Create an isolated workspace with `.claude/skills/<probe>/SKILL.md`
       carrying the candidate description.
    2. Run `claude -p` from that workspace to get a response to `query`.
    3. Run a judge `claude -p` call to classify TRIGGERED vs NOT_TRIGGERED.
    4. Clean up the workspace.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-probe-{unique_id}"

    workspace = Path(tempfile.mkdtemp(prefix=f"run-eval-{unique_id}-"))
    judge_workspace = Path(tempfile.mkdtemp(prefix=f"run-eval-judge-{unique_id}-"))
    skill_dir = workspace / ".claude" / "skills" / clean_name

    try:
        skill_dir.mkdir(parents=True, exist_ok=True)
        indented_desc = "\n  ".join(skill_description.split("\n"))
        (skill_dir / "SKILL.md").write_text(
            f"---\n"
            f"name: {clean_name}\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )

        response = _call_claude(query, cwd=str(workspace), timeout=timeout, model=model)

        # Judge runs with an empty .claude/ workspace so the probe skill doesn't
        # leak into the judge's own context.
        (judge_workspace / ".claude").mkdir(parents=True, exist_ok=True)
        return _judge_response(
            skill_name=skill_name,
            skill_description=skill_description,
            query=query,
            response=response,
            judge_cwd=str(judge_workspace),
            timeout=judge_timeout,
            model=judge_model,
        )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
        shutil.rmtree(judge_workspace, ignore_errors=True)


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    judge_model: str | None = None,
    judge_timeout: int = 60,
) -> dict:
    """Run the full eval set and return results."""
    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    judge_timeout,
                    str(project_root),
                    model,
                    judge_model,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=6, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=90, help="Timeout per probe claude -p call (seconds)")
    parser.add_argument("--judge-timeout", type=int, default=60, help="Timeout per judge claude -p call (seconds)")
    parser.add_argument("--runs-per-query", type=int, default=2, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold for PASS/FAIL")
    parser.add_argument("--model", default=None, help="Model override for probe claude -p (default: user's configured model)")
    parser.add_argument("--judge-model", default=None, help="Model override for the judge claude -p (default: user's configured model)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Evaluating skill '{name}' with description:", file=sys.stderr)
        print(f"  {description}", file=sys.stderr)
        print(f"Eval set: {len(eval_set)} queries x {args.runs_per_query} runs", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        judge_model=args.judge_model,
        judge_timeout=args.judge_timeout,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"\nResults: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
