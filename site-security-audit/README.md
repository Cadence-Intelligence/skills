# Site Security Audit

Security audit for deployed web apps. Give it a URL and it auto-detects the stack, then runs targeted checks.

**Activates when:** You want to audit a live site for vulnerabilities, check if your deployed app is secure, or find exposed credentials and missing auth.

**Example usage:**

"Audit this URL for security issues"
"Is my Vercel app secure?"
"Find vulnerabilities in my deployed site"
"Check my Supabase project for exposed data"

- Auto-detects: Vercel, Supabase, Cloudflare Workers, Firebase, Next.js, Nuxt, Hono, Express
- Seven phases: secrets in JS bundles, API auth testing, CRUD without auth, input validation (SQLi/XSS/NoSQLi), security headers, dependency audit, sensitive data exposure
- Finds hardcoded API keys, exposed credentials, missing auth, IDOR, CORS misconfigurations
- Stack-specific fix guides for Supabase, Cloudflare Workers, Better Auth

For skill file security, use [check-skill-security](../check-skill-security/) instead.

## Install

```bash
/plugin install site-security-audit@cadence
```

Or manually:

```bash
git clone https://github.com/Cadence-Intelligence/skills.git
cd skills && ./install.sh site-security-audit
```

## License

CC BY-NC 4.0, Cadence Intelligence, 2026
