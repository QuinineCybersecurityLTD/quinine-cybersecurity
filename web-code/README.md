# Web & Code Pen-Testing Track

A hands-on playbook for four code/web security tools, added alongside the lab's AI-tools track.
Each tool has a one-page playbook answering six questions (purpose, command, findings, how to read
it, hand-reproduction, noise) with OWASP mappings. **Run the tool first, then write the page.**

## Targets (local only — nothing live)
- **Code tools** → `targets/sample-vulnerable-repo/` — a synthetic repo with fake secrets planted in
  git history and insecure code at HEAD. **Swap in the real shared repo** by replacing that directory.
- **Web tools** → **OWASP Juice Shop** on `http://127.0.0.1:3000` (`targets/juice-shop/`, started with
  `scripts/start_juiceshop.sh`).

## Tools & how they were installed
| Tool | Version | Install | Runner |
|---|---|---|---|
| TruffleHog | 3.99.7 | binary in `web-code/tools/trufflehog/` | `scripts/run_trufflehog.sh [repo]` |
| Semgrep | 1.182.1 | pip (reused from tools venv) | `scripts/run_semgrep.sh [repo]` |
| Nuclei | 3.11.1 | binary in `web-code/tools/nuclei/` | `scripts/run_nuclei.sh [url]` |
| Burp Suite | Community | GUI (needs Java; see page 4) | manual + `evidence/burp/` curl repro |

## Playbook pages
1. `playbook/1-trufflehog.md` — secrets in git history
2. `playbook/2-semgrep.md` — insecure code patterns (SAST)
3. `playbook/3-nuclei.md` — known-vuln templates vs a running app (DAST)
4. `playbook/4-burp.md` — intercept & modify live traffic

## Evidence
Raw tool output is under `web-code/evidence/<tool>/`. Every finding in a page is backed by a file there.

## Reproduce the whole track
```bash
# code tools (work offline)
web-code/scripts/run_trufflehog.sh
web-code/scripts/run_semgrep.sh
# web tools (need Juice Shop running)
web-code/scripts/start_juiceshop.sh &        # http://127.0.0.1:3000
web-code/scripts/run_nuclei.sh http://127.0.0.1:3000
# Burp: launch the GUI, proxy the browser, follow playbook/4-burp.md
```

## Scope & safety
All targets are loopback/local. The sample repo's secrets are **fake**. TruffleHog verification is
disabled on the fixture (`--no-verification`) so nothing is sent to AWS/GitHub; drop that flag on a
real repo. Do not point these tools at any system you are not authorised to test.
