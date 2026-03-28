# Check Skill Security

Audit any skill file before you install it. Pass a `.skill` archive, a folder path, or anything from the marketplace and get a structured security report.

**Activates when:** You want to verify a skill is safe before installing it, or you received a skill from an untrusted source.

**Example usage:**

"Is this skill safe to install?"
"Audit this .skill file before I add it"
"Check this before I install it"

- Six audit phases: prompt injection, data exfiltration, obfuscation, supply chain, persistence, tool poisoning
- Invisible Unicode injection detection (U+E0000-U+E007F, invisible to humans, readable by LLMs)
- Checks for credential file access, env var harvesting, webhook exfiltration, curl-pipe-shell
- Four severity levels: CLEAR / REVIEW / CAUTION / BLOCK
- Standalone scanner: `python3 scripts/audit.py /path/to/skill` (exit codes: 0=CLEAR, 1=REVIEW, 2=CAUTION, 3=BLOCK)

For live web app security, use [site-security-audit](../site-security-audit/) instead.

## Install

```bash
/plugin install check-skill-security@cadence
```

Or manually:

```bash
git clone https://github.com/Cadence-Intelligence/skills.git
cd skills && ./install.sh check-skill-security
```

## License

CC BY-NC 4.0, Cadence Intelligence, 2026
