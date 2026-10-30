# Playbook — Semgrep

**Tool:** Semgrep 1.182.1 (OSS) · **Target:** `targets/sample-vulnerable-repo` (synthetic fixture)
**Run date:** 2026-10-26 · **Evidence:** `web-code/evidence/semgrep/semgrep-sample-repo.json`, `semgrep.log`

### 1. What is this tool for?
It reads source code and flags insecure patterns (injection, weak crypto, misconfig) by matching
rules against the code's structure — fast SAST, no running app needed.

### 2. What command did I run, and against what?
```bash
semgrep scan --config p/security-audit --config p/python --oss-only --metrics off \
    --json -o evidence/semgrep-sample-repo.json  targets/sample-vulnerable-repo
```
`p/security-audit` + `p/python` are curated public rule packs (200 rules here).

### 3. What did it find?
10 findings in `vulnerable_app.py` (5 ERROR, 5 WARNING):

| # | Rule | Line | Issue | OWASP |
|---|---|---|---|---|
| 1 | tainted-sql-string | 11 | SQL built by string concatenation from `request.args` | A03:2021 Injection |
| 2–4 | subprocess-injection / dangerous-subprocess-use / subprocess-shell-true | 17 | OS command from user input with `shell=True` | A03:2021 Injection |
| 5–7 | eval-injection / user-eval / eval-detected | 22 | `eval()` of user input | A03:2021 Injection |
| 8 | insecure-hash-algorithm-md5 | 26 | MD5 for password hashing | A02:2021 Cryptographic Failures |
| 9 | avoid_app_run_with_bad_host | 30 | Flask bound to `0.0.0.0` | A01:2021 Broken Access Control |
| 10 | debug-enabled | 30 | Flask `debug=True` (Werkzeug console / RCE) | A05:2021 Security Misconfiguration |

### 4. How do I read the output?
Each result carries `check_id` (rule), `path` + `start.line` (where), `extra.severity`
(ERROR = high-confidence/high-impact, WARNING = review), `extra.message` (why it's risky + fix), and
`extra.metadata.owasp/cwe`. Multiple rules firing on one line (e.g. lines 17 and 22) are the same
underlying bug seen by different packs — **dedupe by (file, line, root cause)**, don't count them as
separate vulnerabilities.

### 5. Can I reproduce one finding by hand?
Line 11, `tainted-sql-string`:
```python
return str(db.execute("SELECT * FROM users WHERE id = '" + uid + "'").fetchall())
```
`uid = request.args.get("id")` flows straight into SQL text. Reproduction logic: a request
`/user?id=' OR '1'='1` yields `... WHERE id = '' OR '1'='1'`, returning all users — classic SQL
injection. (Static-only here; the fixture Flask app isn't run.)

### 6. How noisy was it?
**Low, after de-duplication.** 10 raw findings collapse to **6 distinct bugs** (SQLi, command
injection, eval, MD5, 0.0.0.0 bind, debug). All 6 are real; 0 false positives on this fixture. On
real code expect more noise — the honest reads are: triage ERROR before WARNING, and confirm each by
tracing whether untrusted input actually reaches the sink before calling it a finding.

**OWASP mapping summary:** A03:2021 Injection (SQLi, command, eval), A02:2021 Cryptographic Failures
(MD5), A05:2021 Security Misconfiguration (Flask debug), A01:2021 Broken Access Control (`0.0.0.0`).
