#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///
"""
skill-auditor: Static analysis for Claude .skill files and skill folders.

Usage:
  python3 audit.py <path-to-skill-folder-or-.skill-file>
  uv run audit.py <path-to-skill-folder-or-.skill-file>

Output: JSON results to stdout, diagnostics to stderr.
Exit codes: 0=CLEAR, 1=REVIEW, 2=CAUTION, 3=BLOCK
"""

import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# ── Verdict levels ────────────────────────────────────────────────────────────
CLEAR   = 0
REVIEW  = 1
CAUTION = 2
BLOCK   = 3

VERDICT_LABELS = {CLEAR: "CLEAR", REVIEW: "REVIEW", CAUTION: "CAUTION", BLOCK: "BLOCK"}

@dataclass
class Finding:
    severity: int          # CLEAR/REVIEW/CAUTION/BLOCK
    category: str
    rule_id: str
    message: str
    file: str
    line: int | None = None
    snippet: str | None = None

@dataclass
class AuditResult:
    verdict: int = CLEAR
    findings: list[Finding] = field(default_factory=list)
    files_scanned: list[str] = field(default_factory=list)
    skill_name: str = ""
    skill_description: str = ""

    def add(self, finding: Finding):
        self.findings.append(finding)
        self.verdict = max(self.verdict, finding.severity)


# ── Pattern libraries ─────────────────────────────────────────────────────────

# Prompt injection — patterns that try to override Claude's behavior
INJECTION_PATTERNS = [
    (BLOCK, "INJ-001", r"ignore (all |your |previous |prior )?(instructions?|rules?|guidelines?|constraints?)",
     "Classic prompt injection: ignoring instructions"),
    (BLOCK, "INJ-002", r"(you are|act as|pretend (to be|you are)|roleplay as)\s+(a |an )?(different|new|unrestricted|jailbroken|DAN|evil|uncensored)",
     "Persona hijacking: impersonates unrestricted model"),
    (BLOCK, "INJ-003", r"(system|assistant|human):\s",
     "Injects fake conversation turns (prompt structure abuse)"),
    (BLOCK, "INJ-004", r"<\|im_(start|end)\|>|<\|system\|>|\[INST\]|\[\/INST\]|<<SYS>>",
     "LLM control token injection (Llama/ChatML format)"),
    (CAUTION, "INJ-005", r"(override|bypass|disable|ignore|skip)\s+(safety|security|restriction|filter|guardrail|limit)",
     "Attempts to bypass safety systems"),
    (CAUTION, "INJ-006", r"(do not|don't|never)\s+(tell|inform|warn|ask|confirm|notify)\s+(the user|user)",
     "Instructs Claude to hide actions from user"),
    (CAUTION, "INJ-007", r"without\s+(asking|telling|informing|confirming|notifying)\s+(the user|user)",
     "Instructs Claude to act without user awareness"),
    (REVIEW,  "INJ-008", r"<!--.*?-->",
     "HTML comment (could hide instructions from human readers)"),
    (REVIEW,  "INJ-009", r"\u200b|\u200c|\u200d|\ufeff|\u2060|\u00ad",
     "Zero-width / invisible Unicode characters (instruction hiding)"),
    (REVIEW,  "INJ-010", r"[\u0300-\u036f\u0610-\u061a\u064b-\u065f]{3,}",
     "Excessive combining Unicode diacritics (text obfuscation)"),
]

# Exfiltration — sending data to external systems
EXFIL_PATTERNS = [
    (BLOCK, "EXF-001", r"curl\s+.*(-d\s*['\"]?\$|--data.*\$ENV|--data.*\$HOME|--data.*\$PATH)",
     "curl POSTing environment/system data to external URL"),
    (BLOCK, "EXF-002", r"(curl|wget|fetch|http\.post|requests\.post)\s+.*\.(ngrok\.io|requestbin|webhook\.site|pipedream\.net|beeceptor|hookbin|canarytokens)",
     "Data sent to known exfiltration/webhook collection service"),
    (BLOCK, "EXF-003", r"(cat|read|open)\s+.*(\.ssh/(id_|known|auth)|\.aws/credentials|\.env|/etc/passwd|/etc/shadow)",
     "Reading sensitive credential files"),
    (BLOCK, "EXF-004", r"\$\{?AWS_(ACCESS|SECRET|SESSION)|GITHUB_TOKEN|ANTHROPIC_API_KEY|OPENAI_API_KEY",
     "Accessing known secret environment variable names"),
    (CAUTION, "EXF-005", r"(curl|wget|fetch)\s+.*-X\s*POST",
     "HTTP POST to external URL — verify what data is sent"),
    (CAUTION, "EXF-006", r"env\s*\||printenv\s*\||os\.environ|process\.env",
     "Dumps environment variables — check if sent anywhere"),
    (CAUTION, "EXF-007", r"(glob|find|ls)\s+.*\.(env|pem|key|p12|pfx|cer|crt)\b",
     "Searches for certificate/key files"),
    (REVIEW,  "EXF-008", r"(curl|wget|http)\s+https?://(?!raw\.githubusercontent\.com|api\.github\.com|pypi\.org|npmjs\.com)",
     "Network request to non-standard domain — verify intent"),
]

# Sensitive file access
SENSITIVE_PATH_PATTERNS = [
    (BLOCK, "PATH-001", r"~/\.ssh|/root/\.ssh|~/.gnupg",
     "Accessing SSH key directory"),
    (BLOCK, "PATH-002", r"~/.aws|~/.azure|~/.gcloud|~/.config/gcloud",
     "Accessing cloud credential directory"),
    (BLOCK, "PATH-003", r"~/.netrc|~/.pgpass|~/.gitconfig",
     "Accessing credential config files"),
    (CAUTION, "PATH-004", r"~/Library/Keychains|/var/lib/dpkg|/etc/shadow",
     "Accessing system keychain or sensitive system paths"),
    (CAUTION, "PATH-005", r"\.env\b(?!ironment)",
     "Accessing .env file — verify it's not being exfiltrated"),
    (REVIEW,  "PATH-006", r"(~|HOME|USERPROFILE)/\.",
     "Accessing hidden files in home directory"),
]

# Code obfuscation
OBFUSCATION_PATTERNS = [
    (BLOCK, "OBF-001", r"(eval|exec)\s*\(\s*(base64|b64|decode|decompress)",
     "Executing base64-decoded code (common obfuscation)"),
    (BLOCK, "OBF-002", r"python3?\s+-c\s+['\"].*\\x[0-9a-f]{2}",
     "Hex-encoded Python one-liner"),
    (BLOCK, "OBF-003", r"\|\s*base64\s+-d\s*\|\s*(bash|sh|python|perl|ruby)",
     "Piping base64-decoded content to shell (backdoor pattern)"),
    (BLOCK, "OBF-004", r"bash\s+-c\s+['\"].*\$\([^)]+\)['\"]",
     "Command substitution in bash -c (execution hiding)"),
    (CAUTION, "OBF-005", r"([A-Za-z0-9+/]{60,}={0,2})\b",
     "Long base64-like string — may be obfuscated code"),
    (CAUTION, "OBF-006", r"chr\s*\(\s*\d+\s*\)\s*\+",
     "Character code concatenation (string obfuscation)"),
    (REVIEW,  "OBF-007", r"\\u[0-9a-fA-F]{4}(\\u[0-9a-fA-F]{4}){4,}",
     "Long sequence of Unicode escapes — possible obfuscation"),
]

# Supply chain / dependency attacks
SUPPLY_CHAIN_PATTERNS = [
    (BLOCK, "DEP-001", r"pip install\s+.*--index-url\s+(?!https://pypi\.org)",
     "pip install from non-PyPI index (possible supply chain attack)"),
    (BLOCK, "DEP-002", r"npm install\s+.*--registry\s+(?!https://registry\.npmjs\.org)",
     "npm install from non-official registry"),
    (BLOCK, "DEP-003", r"curl\s+https?://[^/]+/[^|]+\|\s*(bash|sh|python)",
     "Curl-pipe-shell (untrusted remote code execution)"),
    (CAUTION, "DEP-004", r"pip install\s+(?!-r )([\w-]+)",
     "Direct package install — verify package names for typosquatting"),
    (CAUTION, "DEP-005", r"npm install\s+(?!-g )([\w@/-]+)",
     "Direct npm install — verify package names"),
    (REVIEW,  "DEP-006", r"git clone\s+https?://(?!github\.com/anthropics)",
     "Cloning from non-Anthropic GitHub repo"),
]

# Excessive autonomy / permission abuse
AUTONOMY_PATTERNS = [
    (BLOCK, "AUT-001", r"(modify|edit|update|overwrite)\s+(claude\.md|settings\.json|settings\.local\.json|keybindings\.json)",
     "Modifies Claude Code configuration files (persistence mechanism)"),
    (BLOCK, "AUT-002", r"(add|append|write)\s+.*(~/.bash|~/.zsh|~/.profile|~/.bashrc|~/.zshrc)",
     "Modifies shell config (persistence/backdoor)"),
    (CAUTION, "AUT-003", r"(rm|rmdir|del|unlink|shutil\.rmtree)\s+(-rf?|--recursive)",
     "Destructive file deletion — verify scope"),
    (CAUTION, "AUT-004", r"allowed-tools:\s*(Bash|.*Bash)",
     "Requests Bash tool access — required for some skills, but verify necessity"),
    (CAUTION, "AUT-005", r"(chmod|chown)\s+[0-7]{3,4}|chmod\s+\+x",
     "Changes file permissions"),
    (REVIEW,  "AUT-006", r"(sudo|su |doas )",
     "Uses privilege escalation"),
    (REVIEW,  "AUT-007", r"(cron|launchd|systemd|at \d)",
     "Schedules tasks via system scheduler"),
]

# Reconnaissance patterns
RECON_PATTERNS = [
    (CAUTION, "REC-001", r"(uname|whoami|hostname|id\s*&&|ip\s+addr|ifconfig|netstat)\s",
     "System fingerprinting commands"),
    (CAUTION, "REC-002", r"(find|ls)\s+.*(~|HOME|USERPROFILE)\s.*-name.*\*\.(key|pem|env|json|cfg|conf|ini|toml|yaml|yml)",
     "Searching home directory for sensitive config files"),
    (CAUTION, "REC-003", r"(ps\s+(aux|ef)|lsof\s+-i|netstat\s+-an)",
     "Enumerating running processes or network connections"),
    (REVIEW,  "REC-004", r"(cat|type)\s+/proc/(version|cpuinfo|meminfo|net/)",
     "Reading /proc filesystem (system info gathering)"),
]

# Social engineering
SOCIAL_PATTERNS = [
    (BLOCK, "SOC-001", r"(tell|assure|convince|inform)\s+(the user|user)\s+(this is|it is|that it is)\s+(safe|secure|trusted|verified|official)",
     "Instructs Claude to falsely reassure the user about safety"),
    (CAUTION, "SOC-002", r"(anthropic|claude\.ai|official|verified|certified|trusted)\s+(skill|plugin|extension)",
     "Claims official/trusted status — verify the source"),
    (CAUTION, "SOC-003", r"(require|need|must have|you need)\s+(your|the)\s+(api key|password|token|credential|secret)",
     "Requests credentials from user"),
]

ALL_PATTERN_GROUPS = [
    ("Prompt Injection", INJECTION_PATTERNS),
    ("Data Exfiltration", EXFIL_PATTERNS),
    ("Sensitive Path Access", SENSITIVE_PATH_PATTERNS),
    ("Code Obfuscation", OBFUSCATION_PATTERNS),
    ("Supply Chain", SUPPLY_CHAIN_PATTERNS),
    ("Excessive Autonomy", AUTONOMY_PATTERNS),
    ("Reconnaissance", RECON_PATTERNS),
    ("Social Engineering", SOCIAL_PATTERNS),
]


# ── Scanning logic ─────────────────────────────────────────────────────────────

def scan_text(content: str, filename: str, result: AuditResult):
    lines = content.splitlines()
    for category, patterns in ALL_PATTERN_GROUPS:
        for severity, rule_id, pattern, message in patterns:
            flags = re.IGNORECASE | re.UNICODE
            if rule_id in ("INJ-009",):  # Unicode patterns: no IGNORECASE confusion
                flags = re.UNICODE
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, flags):
                    snippet = line.strip()[:120]
                    result.add(Finding(
                        severity=severity,
                        category=category,
                        rule_id=rule_id,
                        message=message,
                        file=filename,
                        line=i,
                        snippet=snippet,
                    ))
                    break  # One finding per rule per file to avoid noise


def check_frontmatter(content: str, filename: str, result: AuditResult):
    """Validate YAML frontmatter for anomalies."""
    import yaml

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return

    try:
        fm = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        result.add(Finding(
            severity=CAUTION,
            category="Frontmatter",
            rule_id="FM-001",
            message=f"Invalid or suspicious YAML frontmatter: {e}",
            file=filename,
        ))
        return

    if not isinstance(fm, dict):
        return

    # Allowed-tools: Bash without clear justification in description
    allowed = fm.get("allowed-tools", "")
    if "Bash" in str(allowed):
        desc = str(fm.get("description", ""))
        result.add(Finding(
            severity=REVIEW,
            category="Permissions",
            rule_id="FM-002",
            message="allowed-tools includes Bash — verify it's required for stated purpose",
            file=filename,
        ))

    # Suspiciously long description (injection padding)
    desc = str(fm.get("description", ""))
    if len(desc) > 900:
        result.add(Finding(
            severity=REVIEW,
            category="Frontmatter",
            rule_id="FM-003",
            message=f"Description is unusually long ({len(desc)} chars, max 1024) — may contain hidden instructions",
            file=filename,
        ))

    # Unknown/unexpected frontmatter keys
    known_keys = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    extras = set(fm.keys()) - known_keys
    if extras:
        result.add(Finding(
            severity=REVIEW,
            category="Frontmatter",
            rule_id="FM-004",
            message=f"Unknown frontmatter keys: {', '.join(extras)} — non-standard fields may be parsed unexpectedly",
            file=filename,
        ))


def scan_file(content: str, filename: str, result: AuditResult):
    result.files_scanned.append(filename)
    if filename.endswith("SKILL.md") or filename.endswith(".md"):
        check_frontmatter(content, filename, result)
    scan_text(content, filename, result)


def load_skill(path: Path) -> dict[str, str]:
    """Return {filename: content} for all text files in a skill."""
    files = {}
    SKIP_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".otf", ".zip"}

    if path.suffix == ".skill":
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if Path(name).suffix.lower() in SKIP_EXTS:
                    continue
                try:
                    files[name] = zf.read(name).decode("utf-8", errors="replace")
                except Exception:
                    pass
    elif path.is_dir():
        for f in sorted(path.rglob("*")):
            if not f.is_file():
                continue
            if f.suffix.lower() in SKIP_EXTS:
                continue
            rel = str(f.relative_to(path.parent))
            try:
                files[rel] = f.read_text(errors="replace")
            except Exception:
                pass
    else:
        print(f"Error: {path} is not a .skill file or directory", file=sys.stderr)
        sys.exit(1)

    return files


def extract_skill_meta(files: dict[str, str]) -> tuple[str, str]:
    """Extract name and description from SKILL.md frontmatter."""
    for filename, content in files.items():
        if filename.endswith("SKILL.md"):
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                try:
                    import yaml
                    fm = yaml.safe_load(match.group(1))
                    if isinstance(fm, dict):
                        return fm.get("name", ""), str(fm.get("description", ""))
                except Exception:
                    pass
    return "", ""


# ── Main ──────────────────────────────────────────────────────────────────────

def audit(path: Path) -> AuditResult:
    result = AuditResult()
    files = load_skill(path)
    result.skill_name, result.skill_description = extract_skill_meta(files)

    for filename, content in files.items():
        scan_file(content, filename, result)

    return result


def render_report(result: AuditResult, path: Path) -> str:
    label = VERDICT_LABELS[result.verdict]
    bars = {CLEAR: "█████ CLEAR", REVIEW: "██░░░ REVIEW", CAUTION: "███░░ CAUTION", BLOCK: "█████ BLOCK"}

    lines = [
        f"╔══════════════════════════════════════════════════╗",
        f"║  SKILL SECURITY AUDIT                           ║",
        f"╚══════════════════════════════════════════════════╝",
        f"",
        f"  Skill:    {result.skill_name or path.name}",
        f"  Path:     {path}",
        f"  Files:    {len(result.files_scanned)} scanned",
        f"  Verdict:  {bars[result.verdict]}",
        f"",
    ]

    if not result.findings:
        lines += ["  No concerning patterns found.", ""]
    else:
        by_severity = {BLOCK: [], CAUTION: [], REVIEW: []}
        for f in result.findings:
            by_severity.setdefault(f.severity, []).append(f)

        for sev, label_str in [(BLOCK, "BLOCK"), (CAUTION, "CAUTION"), (REVIEW, "REVIEW")]:
            if not by_severity.get(sev):
                continue
            lines.append(f"  ── {label_str} ({'%d finding' % len(by_severity[sev])}{'s' if len(by_severity[sev]) != 1 else ''}) ──")
            for f in by_severity[sev]:
                loc = f":{f.line}" if f.line else ""
                lines.append(f"  [{f.rule_id}] {f.message}")
                lines.append(f"    File: {f.file}{loc}")
                if f.snippet:
                    lines.append(f"    Line: {f.snippet[:100]}")
                lines.append("")

    lines += [
        f"  Files scanned: {', '.join(result.files_scanned[:6])}",
        f"  {'...' if len(result.files_scanned) > 6 else ''}",
    ]

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 audit.py <skill-folder-or-.skill-file>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    result = audit(path)

    # JSON output
    output = {
        "verdict": VERDICT_LABELS[result.verdict],
        "verdict_code": result.verdict,
        "skill_name": result.skill_name,
        "files_scanned": result.files_scanned,
        "finding_count": len(result.findings),
        "findings": [
            {
                "severity": VERDICT_LABELS[f.severity],
                "category": f.category,
                "rule_id": f.rule_id,
                "message": f.message,
                "file": f.file,
                "line": f.line,
                "snippet": f.snippet,
            }
            for f in result.findings
        ],
    }

    # Human-readable to stderr, JSON to stdout
    print(render_report(result, path), file=sys.stderr)
    print(json.dumps(output, indent=2))

    sys.exit(result.verdict)


if __name__ == "__main__":
    main()
