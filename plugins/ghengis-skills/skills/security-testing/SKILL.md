---
name: security-testing
description: Use when reviewing code for vulnerabilities, performing security assessments, or hardening applications -- covers reconnaissance methodology, OWASP Top 10, CVSS scoring, secure coding patterns, and vulnerability analysis
allowed-tools: Read Grep Glob Bash(grep *) Bash(find *)
---

# Security Testing

Defensive security skill for code review, vulnerability analysis, and application hardening. Covers the full assessment lifecycle: reconnaissance, vulnerability identification, proof-of-concept development, secure remediation, and hardening verification.

This skill is for DEFENSIVE security and AUTHORIZED testing only. Never test against production systems. Never exfiltrate real user data. Always document findings responsibly and follow your organization's security policies.

## When to Use

- **Code reviews** -- checking PRs or codebases for security vulnerabilities
- **Pre-deployment security checks** -- verifying an application before release
- **Security audits** -- systematic assessment of an application's security posture
- **Incident response** -- investigating a suspected vulnerability or breach
- **Hardening** -- adding security controls to an existing application
- **Dependency audits** -- checking third-party libraries for known CVEs

## Phase 1: Reconnaissance

Reconnaissance is the FIRST phase of any security assessment. Broad discovery before deep analysis. Map the attack surface systematically before looking for specific vulnerabilities.

### Attack Surface Categories

| Surface | What to Map |
|---------|-------------|
| **Network** | Open ports, exposed services, API endpoints |
| **Authentication** | Login flows, token handling, session management |
| **Data** | Inputs accepted, outputs returned, data stored |
| **Dependencies** | Third-party libraries, their versions, known CVEs |
| **Configuration** | Environment variables, secrets, default credentials |

### Endpoint Discovery

1. Search for route files by pattern:
   - Python (FastAPI): `*routes*.py`, `*router*.py`, `*api*.py`
   - Express: `*routes*.js`, `*router*.js`
   - Flask: files containing `@app.route` or `@blueprint.route`
2. For each route file, identify:
   - HTTP method and path
   - Whether auth is required (look for auth decorators/middleware per-route)
   - What input it accepts (body, query params, headers, file uploads)
3. Search for dynamically registered routes: `include_router`, `app.mount`, `APIRouter(prefix=...)`
4. Check for hidden endpoints: `/debug`, `/admin`, `/internal`, `/_health`, `/metrics`
5. Separately audit WebSocket endpoints (they often lack auth)

### Authentication Mapping

1. Search for auth-related patterns: `auth`, `login`, `token`, `session`, `password`, `jwt`, `oauth`
2. Trace the auth middleware: where is it defined, what does it check, which endpoints use it
3. Classify each endpoint as protected or public
4. Check for: hardcoded tokens, default passwords, disabled auth in dev mode
5. Verify token expiry, refresh mechanisms, revocation capability
6. Map OAuth flows: providers, callback URLs, token storage

### Common Route Patterns to Search

```python
# FastAPI
@app.get("/path")
@router.post("/path")
router = APIRouter(prefix="/api")
app.include_router(router)
Depends(require_auth)
dependencies=[Depends(require_auth)]

# Express
app.get("/path")
router.post("/path")
app.use("/prefix", router)
app.use(authMiddleware)

# Flask
@app.route("/path", methods=["GET"])
@blueprint.route("/path")
@login_required
@jwt_required()
```

### Data Flow Tracing

For each endpoint:
1. What input does it accept? (body, query params, headers, files)
2. How is input validated? (Pydantic models, Zod schemas, manual checks, none?)
3. Where does data go? (database, file system, external API, log)
4. What does it return? (raw data, sanitized, error details?)
5. Flag: unvalidated input, raw error messages, SQL in f-strings

### Dependency Audit

1. Find dependency manifests:
   - Python: `requirements.txt`, `pyproject.toml`, `Pipfile`
   - Node: `package.json`, `package-lock.json`
   - Go: `go.mod`
   - Rust: `Cargo.toml`
2. Run audit tools:
   - Python: `pip audit` or `safety check`
   - Node: `npm audit`
   - Go: `govulncheck`
3. Flag: outdated packages, packages with critical CVEs, transitive dependency risks

### Configuration Review

1. Search for config files: `.env*`, `*config*`, `*settings*`
2. Search for secret patterns:
   - `(?i)(api[_-]?key|secret|password|token|credential|auth)`
   - `(?i)(private[_-]?key|access[_-]?key|client[_-]?secret)`
   - Long base64-like strings: `[A-Za-z0-9+/]{40,}`
   - Provider-specific patterns: `sk-[A-Za-z0-9]{32,}` (OpenAI), `ghp_[A-Za-z0-9]{36}` (GitHub)
3. Verify secrets are loaded from environment variables, not hardcoded
4. Check for dangerous defaults: `secret_key = "changeme"`, `DEBUG = True`
5. Check Docker/CI configs for embedded secrets: `Dockerfile`, `docker-compose.yml`, `.github/workflows/*.yml`
6. Verify `.env.example` does not contain real values

### Recon Pitfalls

- **Missing hidden endpoints**: Only checking main route files but missing dynamically registered routes or admin/debug endpoints
- **Incomplete auth mapping**: Assuming auth is applied globally when it is per-route. Check EACH endpoint individually.
- **Dependency blind spots**: Only checking direct deps, missing transitive ones. Use lock files.
- **Configuration leaks**: `.env` in `.gitignore` but `.env.example` has real values. Docker/CI configs with embedded secrets.

## Phase 2: Vulnerability Analysis

Systematic vulnerability identification organized by severity and OWASP Top 10 alignment.

### Critical Vulnerabilities (CVSS 9.0-10.0)

**SQL Injection** -- String concatenation in queries, f-strings with user input near database calls.
```python
# VULNERABLE
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# SAFE
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

**Command Injection** -- `os.system()`, `subprocess` with `shell=True` and user input.
```python
# VULNERABLE
subprocess.run(f"grep {user_input} file.txt", shell=True)
# SAFE
subprocess.run(["grep", user_input, "file.txt"], shell=False)
```

**Authentication Bypass** -- Missing auth checks on endpoints, JWT without signature verification.

**Remote Code Execution** -- `eval()`, `exec()`, `pickle.loads()` on user-controlled input.

### High Vulnerabilities (CVSS 7.0-8.9)

**Cross-Site Scripting (XSS)** -- `innerHTML`, `dangerouslySetInnerHTML`, unescaped template output.
```python
# VULNERABLE
return f"<p>{user_comment}</p>"
# SAFE
from markupsafe import escape
return f"<p>{escape(user_comment)}</p>"
```

**Server-Side Request Forgery (SSRF)** -- HTTP requests with user-controlled URLs without allowlist validation.

**Path Traversal** -- File operations with user-controlled paths.
```python
# VULNERABLE
with open(os.path.join(base, user_path)) as f: ...
# SAFE
resolved = Path(base).joinpath(user_path).resolve()
if not resolved.is_relative_to(Path(base).resolve()):
    raise ValueError("Path traversal detected")
```

**Secrets in Code** -- Hardcoded API keys, passwords, tokens committed to source control.

**Insecure Deserialization** -- `yaml.load()` (without SafeLoader), `pickle` on untrusted data.

### Medium Vulnerabilities (CVSS 4.0-6.9)

- **Weak Cryptography**: MD5/SHA1 for passwords, DES, RC4
- **Missing Rate Limiting**: Auth endpoints without throttling
- **Verbose Error Messages**: Stack traces returned to users in production
- **CORS Misconfiguration**: `Access-Control-Allow-Origin: *` combined with credentials

### Low Vulnerabilities (CVSS 0.1-3.9)

- **Debug Mode in Production**: `DEBUG=True`, verbose logging
- **Missing Security Headers**: No CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **Outdated Dependencies**: Known CVEs in packages without active exploits

### Analysis Pattern

1. Map the attack surface (use Phase 1 recon output)
2. Trace data flow from each input to dangerous sinks
3. Check each input handling point against the vulnerability categories above
4. Verify authentication and authorization on every endpoint
5. Review dependency versions against CVE databases

### Vulnerability Output Format

For each vulnerability found, document it precisely:

```
VULN_ID: [type]-[sequential] (e.g., SQLI-001, XSS-002)
TYPE: sql_injection | xss | auth_bypass | command_injection | path_traversal | ssrf | rce | ...
SEVERITY: CRITICAL | HIGH | MEDIUM | LOW
CVSS_ESTIMATE: [score]/10
FILE: [path:line_number]
DESCRIPTION: [What is wrong, specifically]
DATA_FLOW: [Input source] -> [Processing] -> [Dangerous sink]
PROOF: [How to exploit -- specific steps]
FIX: [How to remediate]
```

## Phase 3: CVSS Scoring

Use CVSS (Common Vulnerability Scoring System) to rate severity consistently.

| Score | Severity | Response |
|-------|----------|----------|
| 9.0-10.0 | Critical | Flag immediately, recommend immediate patch |
| 7.0-8.9 | High | Flag, recommend patching within days |
| 4.0-6.9 | Medium | Note, recommend patching in next sprint |
| 1.0-3.9 | Low | Document, address when convenient |
| 0.0-0.9 | Informational | Document for completeness |

### CVSS Factors to Consider

- **Attack Vector**: Network (remote) vs. Local vs. Physical
- **Attack Complexity**: Low (easy to exploit) vs. High (requires special conditions)
- **Privileges Required**: None vs. Low vs. High
- **User Interaction**: None vs. Required
- **Impact**: Confidentiality, Integrity, Availability (each rated None/Low/High)

### Vulnerability Categories

The following categories map to common finding types:

| Category | Description | Typical CVSS |
|----------|-------------|-------------|
| `default_credentials` | Factory/default passwords still active | 8.0-9.5 |
| `open_port` | Unnecessary services exposed | 4.0-7.0 |
| `unencrypted_traffic` | Sensitive data transmitted in cleartext | 5.0-8.0 |
| `outdated_firmware` | Known CVEs in running software versions | 5.0-10.0 |
| `misconfiguration` | Insecure settings, overly permissive access | 3.0-8.0 |
| `known_cve` | Published CVE with available exploit | 4.0-10.0 |

## Phase 4: Exploit Proof Methodology

Proving vulnerabilities are REAL with working proof-of-concept. Proofs, not alerts -- a working PoC demonstrates actual exploitability and impact.

### Why Proofs Matter

- Static analysis generates false positives
- A working PoC proves the vulnerability is exploitable
- PoCs demonstrate actual impact to stakeholders
- Proofs prioritize remediation efforts (real > theoretical)

### PoC Development Pattern

1. **Confirm the vulnerability**: Read the code to understand the exact flaw. Identify the input vector (URL param, form field, API body). Trace data flow to the dangerous sink.
2. **Craft the exploit**: Start with the simplest possible payload. Escalate complexity only if needed. Test in isolation (never against production).
3. **Document reproduction steps**:
   ```
   STEP 1: [Setup/prerequisites]
   STEP 2: [Send this exact request]
   STEP 3: [Observe this response/behavior]
   EXPECTED: [What should happen if not vulnerable]
   ACTUAL: [What actually happens -- proving the vulnerability]
   ```
4. **Assess impact**: What data is exposed? Can the attacker escalate privileges? What is the blast radius? Estimate CVSS score.

### Safe Exploitation Rules

- ONLY test against local/development instances
- NEVER modify production data
- NEVER exfiltrate real user data
- Use benign payloads (`alert('xss')`, not data theft scripts)
- Document everything for audit trail

### PoC Output Format

```
VULN_ID: [reference to vulnerability finding]
POC_STATUS: CONFIRMED | NOT_EXPLOITABLE | NEEDS_MORE_TESTING
REPRODUCTION:
  1. [Step]
  2. [Step]
  3. [Step]
PAYLOAD: [exact payload used]
RESPONSE: [what happened]
IMPACT: [what an attacker could achieve]
CVSS_ESTIMATE: [score]/10
```

## Phase 5: Secure Remediation

Write security fixes that remediate vulnerabilities WITHOUT breaking functionality.

### Fix Patterns

**SQL Injection** -> Parameterized queries:
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

**Command Injection** -> Avoid `shell=True`, use argument lists:
```python
subprocess.run(["grep", user_input, "file.txt"], shell=False)
```

**XSS** -> Escape output, use safe APIs:
```python
from markupsafe import escape
return f"<p>{escape(user_comment)}</p>"
```

**Path Traversal** -> Validate and resolve paths:
```python
resolved = Path(base).joinpath(user_path).resolve()
if not resolved.is_relative_to(Path(base).resolve()):
    raise ValueError("Path traversal detected")
```

**Secrets** -> Environment variables, never hardcoded:
```python
API_KEY = os.environ.get("API_KEY")
```

### Fix Rules

1. **Minimal diff**: Change only what is needed to fix the vulnerability
2. **Do not break functionality**: Run existing tests after patching
3. **Defense in depth**: Fix the root cause AND add input validation
4. **Test the fix**: Verify the original PoC no longer works
5. **Document the change**: Comment explaining why the fix was needed

### Fix Validation Checklist

- [ ] Original exploit payload no longer works
- [ ] Legitimate use cases still function correctly
- [ ] No new vulnerabilities introduced by the fix
- [ ] Tests pass after the change
- [ ] Fix follows existing code style and patterns

## Hardening Checklist

Comprehensive checklist for application hardening. Use after vulnerability remediation or during pre-deployment review.

### HTTP Security Headers

- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY` (or `SAMEORIGIN` if framing is needed)
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] `Permissions-Policy` (restrict camera, microphone, geolocation)
- [ ] `Content-Security-Policy` (restrict script/style sources)
- [ ] `Strict-Transport-Security` (HSTS, include subdomains)

### CORS

- [ ] No `Access-Control-Allow-Origin: *` with credentials
- [ ] Origin allowlist is explicit, not wildcard
- [ ] Preflight requests handled correctly

### Authentication

- [ ] Every endpoint checked individually for auth requirements
- [ ] WebSocket endpoints have auth (checked BEFORE `accept()`)
- [ ] Token expiry is enforced
- [ ] Password reset flows are secure (time-limited tokens, no user enumeration)
- [ ] Session management is secure (HttpOnly, Secure, SameSite cookies)

### Rate Limiting

- [ ] Auth endpoints (login, register, password reset) are rate limited
- [ ] API endpoints with LLM/compute cost are rate limited
- [ ] Rate limits are per-IP or per-user, not global

### Input Sanitization

- [ ] All user input is validated before use
- [ ] Control characters stripped from text inputs
- [ ] Input length limits enforced
- [ ] File upload size and type limits enforced
- [ ] SQL queries use parameterized statements exclusively
- [ ] Shell commands use argument lists, never string interpolation

### Dependency Management

- [ ] No known critical CVEs in direct dependencies
- [ ] Lock files committed and up to date
- [ ] Dependency audit tool in CI pipeline
- [ ] Transitive dependencies reviewed

### Secrets Management

- [ ] No secrets in source code
- [ ] No secrets in `.env.example` or Docker configs
- [ ] Secrets loaded from environment variables or secret manager
- [ ] No default secrets that work in production

### OWASP IoT Top 10

When assessing IoT or embedded systems, additionally check:

1. **Weak, Guessable, or Hardcoded Passwords** -- Default credentials still active
2. **Insecure Network Services** -- Unnecessary open ports, unencrypted services
3. **Insecure Ecosystem Interfaces** -- Web/API/cloud/mobile interfaces lacking auth
4. **Lack of Secure Update Mechanism** -- No firmware signing, no update verification
5. **Use of Insecure or Outdated Components** -- Known CVEs in firmware/libraries
6. **Insufficient Privacy Protection** -- Personal data stored/transmitted insecurely
7. **Insecure Data Transfer and Storage** -- Cleartext protocols (MQTT without TLS, HTTP)
8. **Lack of Device Management** -- No inventory, no monitoring, no decommissioning
9. **Insecure Default Settings** -- Debug mode enabled, verbose logging, open ports by default
10. **Lack of Physical Hardening** -- Exposed debug ports (JTAG, UART), removable storage

## Security Assessment Report Format

Structure findings into a report that stakeholders can act on:

```markdown
## Executive Summary
[2-3 sentences: scope, critical finding count, overall risk level]

## Findings by Severity

### Critical
[List with VULN_ID, description, file:line, fix recommendation]

### High
[Same format]

### Medium / Low
[Same format, can be condensed]

## Remediation Plan (Prioritized)
1. [Fix critical findings immediately]
2. [Fix high findings within N days]
3. [Address medium findings in next sprint]
4. [Track low findings in backlog]

## Attack Surface Summary
[Endpoints discovered, auth coverage, dependency health]
```

## Anti-Patterns

| If you notice... | The problem is... | Fix it by... |
|-----------------|-------------------|-------------|
| Reporting dozens of "possible" vulnerabilities without PoCs | Alert fatigue, false positive noise | Confirming each finding with a proof or marking confidence level |
| Only checking for SQL injection and XSS | Incomplete coverage | Systematically checking against the full OWASP Top 10 |
| Recommending "use a WAF" as the fix | Treating symptoms, not root causes | Fixing the vulnerable code AND recommending defense-in-depth |
| Skipping dependency audit | Blind spot for supply chain attacks | Running `pip audit` / `npm audit` as part of every assessment |
| Testing against production | Ethical and legal risk | ALWAYS using local/dev environments for PoC testing |
| Reporting a vulnerability without a fix | Incomplete finding | Every vulnerability report must include a specific remediation |
