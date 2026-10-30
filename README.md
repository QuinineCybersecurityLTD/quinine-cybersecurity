# Local AI Penetration Testing Lab — Playbook & Reproduction Guide

This repository contains an autonomous, hands-on AI penetration testing lab targeting a local Ollama model (`lab-guard`) using four industry-standard security evaluation tools:
1. **Garak** (NVIDIA LLM Vulnerability Scanner)
2. **Promptfoo** (Adversarial Evaluation Framework)
3. **Microsoft PyRIT** (Python Risk Identification Tool)
4. **AISI Inspect** (UK AI Security Institute Evaluation Platform)

**Security Scope:** All testing targets the local Ollama instance on `127.0.0.1:11434` only. Zero data or test prompts are sent to external/cloud model providers. The confidential canary (`LAB-CANARY-731`) is purely synthetic.

---

## 1. Directory Structure

```text
ai-pentest-lab-starter/
├── configs/
│   └── promptfooconfig.yaml         # Promptfoo test suite (6 security test cases)
├── scripts/
│   ├── baseline_test.py             # Pre-flight functional & refusal validation
│   ├── parse_garak.py               # Garak JSONL report parser
│   ├── reproduce_garak.py           # Manual 3-trial reproduction of Attempt 12
│   ├── pyrit_multiturn.py           # PyRIT 3-turn social engineering attack script
│   ├── inspect_lab.py               # AISI Inspect evaluation task definition
│   └── generate_pdf.py              # ReportLab 4-page executive PDF generator
├── evidence/
│   ├── garak/                       # garak-smoke.report.jsonl, garak.log, manual_reproduction.json
│   ├── promptfoo/                   # promptfoo-results.json
│   ├── pyrit/                       # pyrit_result.json
│   └── inspect/                     # Inspect AI raw JSON evaluation run log
├── reports/
│   ├── 01_Garak.md                  # Garak one-page playbook report
│   ├── 02_Promptfoo.md              # Promptfoo one-page playbook report
│   ├── 03_PyRIT.md                  # PyRIT one-page playbook report
│   ├── 04_Inspect.md                # AISI Inspect one-page playbook report
│   └── AI_Penetration_Testing_Playbook.pdf  # Final compiled 4-page A4 PDF submission
├── results/
│   ├── findings.csv                 # OWASP Top 10 (2026) triage matrix
│   └── false_positives.md           # Detector false positive & nuance analysis
├── Modelfile                        # System prompt definition and synthetic canary
├── README.md                        # This reproduction guide
└── EXECUTION_STATUS.md              # Full execution metrics and run status
```

---

## 2. Prerequisites & Environment Setup

Run in Windows PowerShell (or adapt for Linux/macOS):

```powershell
# 1. Start Ollama and pull base model
ollama serve
ollama pull llama3.2:3b

# 2. Build the lab-guard target model
ollama create lab-guard -f .\Modelfile

# 3. Verify baseline behavior
python scripts/baseline_test.py
```

### Virtual Environments
To prevent dependency conflicts between ML and security packages:
*   `.venv`: Python 3.11 with `inspect-ai` and `openai`
*   `.venv-garak`: Python 3.11 with `garak` and `torch`
*   `.venv-pyrit`: Python 3.11 with `pyrit`, `openai`, and `reportlab`
*   Node.js: `npm install -g promptfoo`

---

## 3. Step-by-Step Tool Execution

### Tool 1: Garak Vulnerability Scanner
```powershell
.\.venv-garak\Scripts\python.exe -m garak --target_type ollama --target_name lab-guard --spec probes.dan --generations 1 --report_prefix garak-smoke
# Manual reproduction of Attempt 12:
.\.venv\Scripts\python.exe scripts/reproduce_garak.py
```

### Tool 2: Promptfoo
```powershell
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
$env:PROMPTFOO_DISABLE_REMOTE_GENERATION="true"
$env:PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION="true"
$env:PROMPTFOO_DISABLE_TELEMETRY="1"

promptfoo eval -c .\configs\promptfooconfig.yaml -j 1 --no-share --no-cache -o .\evidence\promptfoo\promptfoo-results.json
```

### Tool 3: Microsoft PyRIT Multi-Turn Attack
```powershell
.\.venv-pyrit\Scripts\python.exe .\scripts\pyrit_multiturn.py
```

### Tool 4: AISI Inspect Evaluation
```powershell
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434/v1"
.\.venv\Scripts\inspect.exe eval .\scripts\inspect_lab.py --model ollama/lab-guard --log-dir .\evidence\inspect --log-format json --display plain
```

### PDF Compilation
```powershell
.\.venv-pyrit\Scripts\python.exe .\scripts\generate_pdf.py
```

---

## 4. Summary of Findings (OWASP Top 10 for LLM 2026)

*   **FND-001 (Garak Attempt 12):** `LLM01:2026 Prompt Injection` — Model acknowledged role-play persona override ("DAN Mode enabled") in 7/33 attempts. Confirmed manually in 3/3 trials. Private canary remained protected. (Severity: **Medium**).
*   **Promptfoo (6/6 Pass):** Defended against direct, authority, and Base64 encoded extraction attacks.
*   **PyRIT (Multi-Turn):** 3-turn progressive escalation resulted in hard refusal (`ACCESS DENIED`). No canary leakage.
*   **Inspect AI (3/3 Pass):** Exact-match benchmark achieved **1.000 (100%) accuracy**.
