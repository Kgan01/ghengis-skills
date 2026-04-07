# Security Testing -- Evaluation

## TC-1: Happy Path -- OWASP Top 10 Coverage in Code Review
- **prompt:** "Review this Python FastAPI endpoint for security vulnerabilities:\n```python\n@app.post('/users/search')\nasync def search_users(query: str):\n    result = await db.execute(f'SELECT * FROM users WHERE name LIKE \"%{query}%\"')\n    return {'users': result.fetchall(), 'debug': traceback.format_stack()}\n```"
- **context:** Tests systematic vulnerability identification against OWASP categories. This endpoint has SQL injection (f-string in query), verbose error messages (debug stack trace in response), and missing authentication.
- **assertions:**
  - Identifies SQL injection vulnerability (f-string concatenation in database query) with CRITICAL severity
  - Identifies verbose error message exposure (traceback.format_stack() returned to user) with MEDIUM severity
  - Identifies missing authentication on a data-access endpoint
  - Provides the correct fix for SQL injection: parameterized query using `%s` placeholder
  - Documents each finding using the VULN_ID format with TYPE, SEVERITY, CVSS_ESTIMATE, FILE, DESCRIPTION, DATA_FLOW, PROOF, and FIX
- **passing_grade:** 4/5 assertions must pass

## TC-2: Quality Check -- CVSS Scoring Accuracy
- **prompt:** "Score these three vulnerabilities: 1) SQL injection on a public-facing login endpoint with no authentication required, 2) Missing X-Content-Type-Options header on a static marketing site, 3) SSRF in an internal admin tool that requires VPN + admin credentials to access."
- **context:** Tests CVSS scoring methodology. Each vulnerability has different attack vectors, complexity, and privilege requirements that should produce meaningfully different scores.
- **assertions:**
  - SQL injection scores CRITICAL (9.0-10.0): network attack vector, low complexity, no privileges required, high impact on confidentiality/integrity
  - Missing security header scores LOW (1.0-3.9): informational, no direct exploit, minimal impact
  - SSRF scores MEDIUM (4.0-6.9): requires VPN access (not network-reachable) and high privileges (admin), which significantly reduces the score despite SSRF being typically high severity
  - Each score includes the CVSS factors considered: attack vector, attack complexity, privileges required, user interaction, and impact dimensions
  - Response time recommendations align with severity: critical = immediate patch, low = address when convenient
- **passing_grade:** 4/5 assertions must pass

## TC-3: Happy Path -- Secure Code Review with Fix Patterns
- **prompt:** "Review this Node.js code:\n```javascript\nconst userFile = req.query.filename;\nconst content = fs.readFileSync(path.join('/uploads', userFile));\nconst parsed = yaml.load(content);\nres.send(parsed);\n```"
- **context:** Tests identification of multiple vulnerability types and application of fix patterns. Contains path traversal (user-controlled filename), insecure deserialization (yaml.load without SafeLoader equivalent), and potentially missing auth.
- **assertions:**
  - Identifies path traversal vulnerability: user-controlled `filename` joined to `/uploads` without validation (user could pass `../../etc/passwd`)
  - Identifies insecure YAML deserialization: `yaml.load()` without safe loader can execute arbitrary code
  - Provides the path traversal fix: resolve the path and verify it stays within the base directory
  - Provides the YAML fix: use `yaml.safeLoad()` or equivalent safe parsing method
  - Each vulnerability includes a DATA_FLOW trace: input source (req.query.filename) -> processing -> dangerous sink (readFileSync / yaml.load)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Quality Check -- Exploit Proof Format
- **prompt:** "I found what looks like a command injection in our backup script: `subprocess.run(f'tar -czf {backup_name}.tar.gz /data', shell=True)` where backup_name comes from a user-supplied form field. Write a proof of concept."
- **context:** Tests PoC development methodology: confirm the vulnerability, craft the exploit, document reproduction steps, assess impact, and follow safe exploitation rules.
- **assertions:**
  - Provides a specific malicious payload for backup_name (e.g., `; rm -rf /` or `$(whoami)` to demonstrate injection)
  - Documents reproduction steps in the prescribed format: STEP 1 (setup), STEP 2 (send request), STEP 3 (observe), EXPECTED vs ACTUAL
  - Uses benign payloads for demonstration (as required by safe exploitation rules), not destructive ones
  - Includes POC_STATUS, PAYLOAD, RESPONSE, IMPACT, and CVSS_ESTIMATE fields
  - Provides the fix: replace `shell=True` with argument list format and remove f-string interpolation
- **passing_grade:** 4/5 assertions must pass

## TC-5: Edge Case -- Dependency Audit and Secret Detection
- **prompt:** "Audit this project for supply chain and secrets issues. The requirements.txt pins `pyyaml==5.3.1` and `requests==2.25.0`. I also found this in the codebase: `API_KEY = 'sk-proj-abc123def456ghi789'` and the .env.example file contains `DATABASE_URL=postgres://admin:realpassword@prod-db.example.com/myapp`."
- **context:** Tests dependency audit (outdated packages with known CVEs) and secret detection (hardcoded API key matching provider-specific patterns, real credentials in .env.example).
- **assertions:**
  - Flags the pinned PyYAML and requests versions as outdated with potential known CVEs
  - Identifies the hardcoded API key as a secret in code (matches the `sk-` provider-specific pattern for OpenAI-style keys)
  - Flags the .env.example file containing a real database password (violates the rule that .env.example must not contain real values)
  - Recommends loading secrets from environment variables (`os.environ.get("API_KEY")`) instead of hardcoding
  - Recommends running `pip audit` or `safety check` as part of the CI pipeline for ongoing dependency monitoring
- **passing_grade:** 4/5 assertions must pass
