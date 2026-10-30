# Playbook — TruffleHog

**Tool:** TruffleHog 3.99.7 (trufflesecurity) · **Target:** `targets/sample-vulnerable-repo` (synthetic fixture — swap in the real shared repo)
**Run date:** 2026-10-26 · **Evidence:** `web-code/evidence/trufflehog/trufflehog-sample-repo.json`, `trufflehog.log`

### 1. What is this tool for?
It hunts for secrets — API keys, tokens, passwords — left behind in code **and in a repo's entire git history**.

### 2. What command did I run, and against what?
```bash
./web-code/tools/trufflehog/trufflehog.exe git "file://./targets/sample-vulnerable-repo" \
    --no-update --no-verification --json > evidence/trufflehog-sample-repo.json
```
`git` scans the **full commit history** (not just the working tree). `--no-verification` keeps it
offline (no probe to AWS/GitHub) because the fixture secrets are fake; drop it on a real repo to get
live "verified" checks. Run from the lab root.

### 3. What did it find?
2 unverified secrets, both in commit `556ea8b` → `config.py`:

| Detector | Secret (redacted) | Commit | File:line | Verified |
|---|---|---|---|---|
| AWS | `AKIAZ8LAB3Q7RT2WXYZ9` | 556ea8b | config.py:2 | false |
| Postgres | `postgres://admin:S3cr3t-Lab-Pw…` | 556ea8b | config.py:5 | false |

Scan summary: `chunks:10, bytes:2082, verified:0, unverified:2, 0.41s`.

### 4. How do I read the output?
Each JSON line is one hit: `DetectorName` (what kind of secret), `Verified` (**true = the tool
confirmed the key still works live** — treat as an emergency; false/unverified = matched the pattern
but not live-checked), `Raw`/`Redacted` (the value), and `SourceMetadata.Git` (commit, file, line,
author email, timestamp). The critical point: commit `556ea8b` is **not** HEAD — the secret was
"removed" in a later commit but lives on in history, which is exactly what git-history scanning
catches and a working-tree-only scan misses.

### 5. Can I reproduce one finding by hand?
Yes.
```bash
cd targets/sample-vulnerable-repo
git show 556ea8b:config.py        # AWS key + Postgres URL in plaintext
git show HEAD:config.py           # same file at HEAD: secrets gone (os.environ[...])
```
Output confirmed: the AWS key and DB password are present in the historical blob and absent at HEAD.

### 6. How noisy was it?
**Very low.** 2 hits, both real planted secrets, 0 false positives. Note a precision detail worth
keeping in the playbook: the fixture also contains fake GitHub (`ghp_…`), Slack (`xoxb-…`) and Stripe
(`sk_live_…`) tokens that TruffleHog **did not** flag — its detectors apply structural/checksum
validation, so randomly-typed fakes slip through while genuine tokens fire. On a real repo, treat a
clean result as "no *detectable* secrets", not "no secrets", and always scan history.

**OWASP / weakness mapping:** CWE-798 Hardcoded Credentials; OWASP **A07:2021 Identification & Auth
Failures** and **API8:2023 Security Misconfiguration** (secrets committed to source). Each *verified*
live key would additionally be whatever the key grants (e.g. A01 Broken Access Control to that service).
