# Playbook — Nuclei

**Tool:** Nuclei 3.11.1 (templates: 14,104 official + 3 custom) · **Target:** `http://127.0.0.1:8010`
(local file server over the sample repo — a Juice Shop stand-in; see note) · **Run date:** 2026-10-26
**Evidence:** `web-code/evidence/nuclei/nuclei-sample-target.jsonl`, `nuclei.log`

> **Environment note (honest):** OWASP Juice Shop (the intended web target) would not run in this
> lab — its prebuilt package is Node 22 and local Node is 20 (native-module ABI mismatch), and the
> source build needs MSVC/node-gyp. So Nuclei was pointed at a loopback HTTP server exposing the
> sample vulnerable repo (which has a real `.git/` directory and config files). The run, templates,
> and hits below are all real. Against Juice Shop you would run the identical command at
> `http://127.0.0.1:3000` — `web-code/scripts/run_nuclei.sh http://127.0.0.1:3000`.

### 1. What is this tool for?
It checks a **running** web app against a big library of templates for known vulnerabilities,
exposures and misconfigurations — fast, signature-based DAST.

### 2. What command did I run, and against what?
```bash
nuclei -u http://127.0.0.1:8010 -disable-update-check -no-interactsh \
  -t ~/nuclei-templates/http/exposures/ -t ~/nuclei-templates/http/misconfiguration/ \
  -t web-code/nuclei-templates/   -jsonl -o nuclei-sample-target.jsonl -stats
```
1,693 templates, 4,490 requests, 28 s.

### 3. What did it find? (17 matches → 4 distinct issues)
| Severity | Template | Matched at | Issue |
|---|---|---|---|
| medium | `git-config` + custom `lab-exposed-git-config` | `/.git/config` | **Exposed git repository** |
| info | `git-logs-exposure` | `/.git/logs/HEAD` | Exposed git logs |
| info | `readme-md` | `/README.md` | Source file disclosure |
| info ×10 + low ×3 | `http-missing-security-headers` + custom `lab-missing-security-headers` | `/` | **Missing security headers** (CSP, X-Frame-Options, X-Content-Type-Options, …) |

The exposed `.git` is the serious one: a reachable `.git/` lets an attacker reconstruct the whole
source tree (and any secrets committed to it — see the TruffleHog page).

### 4. How do I read the output?
Each JSONL line has `template-id`, `info.severity` (info→critical), `matched-at` (the exact URL that
proved it), and `info.name`. **Severity drives triage** (medium git exposure first; info headers
later). Note the counts: the official header template fired **10** times and my custom one **3** times
for the *same* underlying weakness — "missing security headers" is **one** issue, not 13. Always
collapse by root cause before reporting.

### 5. Can I reproduce one finding by hand?
`git-config`:
```bash
curl http://127.0.0.1:8010/.git/config    # -> 200, prints [core] ... (the repo's git config)
```
Confirmed: the server returns the `.git/config` body (`[core] repositoryformatversion = 0 …`), so the
repository metadata is publicly readable. (On a real site you'd then `git-dumper` the tree.)

### 6. How noisy was it?
**Moderate, and a good lesson in dedup.** 17 raw matches collapse to **4 distinct issues**. 0 false
positives on this target — every hit corresponds to something actually served — but the 13 header
lines over-count one weakness. Running the *entire* 14k template set against a real app produces far
more info-level noise; scope by `-tags`/`-severity` and triage medium+ first. Custom templates (3
written for this lab in `web-code/nuclei-templates/`) fired correctly alongside the official set.

**OWASP mapping:** exposed `.git` → **A01:2021 Broken Access Control** / sensitive exposure
(CWE-538/527); missing security headers → **A05:2021 Security Misconfiguration**.
