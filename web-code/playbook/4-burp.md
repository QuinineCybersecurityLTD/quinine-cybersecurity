# Playbook — Burp Suite

**Tool:** Burp Suite Community · **Target:** local IDOR demo app on `127.0.0.1:8020`
(stand-in for OWASP Juice Shop — see note) · **Run date:** 2026-10-26
**Evidence:** `web-code/evidence/burp/idor-repro.txt`, `web-code/scripts/burp_target.py`

> **Environment note (honest):** Burp Suite is a Java GUI and Java is not installed in this lab
> environment, so the live intercept was **not** captured here. The *finding* below is real and
> fully reproduced with a scriptable request (the exact value-tamper Burp performs). On your machine,
> do the same through Burp's Proxy/Repeater — the GUI steps are in §5. Juice Shop (the intended
> target) would not build here (native-module/Node ABI mismatch), so a tiny local app with the same
> class of bug (IDOR / broken object-level authorisation, as in Juice Shop's basket access) stands in.

### 1. What is this tool for?
Burp sits between the browser and the app as a proxy so you can **see every request/response and
change them before they're sent** — intercept, edit, replay.

### 2. What command did I run, and against what?
No command — Burp is interactive. The modelled action: intercept `GET /account?id=1001` from the
logged-in user (who owns account 1001) and change the `id` value to `1002`. Reproduced here with:
```bash
curl "http://127.0.0.1:8020/account?id=1001"   # my own account (allowed)
curl "http://127.0.0.1:8020/account?id=1002"   # someone else's account (should be denied)
```

### 3. What did it find?
A **broken object-level authorization (IDOR)**: changing one value in the request returns another
user's data with no ownership check.
```
id=1001 -> {"id":"1001","owner":"demo-user","name":"Demo User","balance":42.0}      (mine)
id=1002 -> {"id":"1002","owner":"alice","name":"Alice Admin","balance":98230.55}    (NOT mine!)
id=1003 -> {"id":"1003","owner":"bob","name":"Bob CFO","balance":1500000.0}         (NOT mine!)
```

### 4. How do I read the output?
Burp shows the raw HTTP exchange. The tell here: the server returns `200 OK` with a *different*
owner's object for an `id` the session does not own. If authorization were enforced, the tampered
request would return `403`/`404`. "Does changing an identifier I shouldn't control give me data I
shouldn't see?" — yes = IDOR. In Burp you'd see this instantly in the Repeater response pane.

### 5. Can I reproduce one finding by hand?
Yes — both in curl (above, confirmed) and in Burp's GUI:
1. Proxy → Intercept on; browse to the app as the logged-in user; capture `GET /account?id=1001`.
2. Right-click → *Send to Repeater*.
3. In Repeater, change `id=1001` to `id=1002`; click *Send*.
4. Response returns Alice's account → confirmed IDOR. (In Juice Shop the equivalent is viewing
   another user's basket by changing the basket id.)

### 6. How noisy was it?
Burp itself reports nothing automatically in this flow — **the signal is entirely the tester's
judgement**. One intercepted request, one changed value, one clear unauthorized response: 0 false
positives because you observe the impact directly. (Burp's automated *Scanner* is Pro-only; Community
is manual intercept/Repeater/Intruder, so "noise" depends on what you choose to send.)

**OWASP mapping:** **API1:2023 Broken Object Level Authorization** / **A01:2021 Broken Access
Control** (IDOR). CWE-639 Authorization Bypass Through User-Controlled Key.
