import json

path = r"C:\Users\Mohit\.local\share\garak\garak_runs\garak-smoke.report.jsonl"
print(f"Reading {path}...")
with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        entry_type = data.get("entry_type")
        if entry_type == "attempt":
            seq = data.get("seq")
            prompt = data.get("prompt", {}).get("turns", [{}])[0].get("content", {}).get("text", "")[:80]
            outputs = [o.get("text", "").strip()[:80] for o in data.get("outputs", [])]
            print(f"[{seq}] PROBE: {data.get('probe_classname')}")
            print(f"     PROMPT: {prompt}...")
            print(f"     RESPONSE: {outputs}")
            print(f"     DETECTOR RESULTS: {data.get('detector_results')}")
        elif entry_type in ("eval", "report", "config"):
            print(f"--> {entry_type}: {data.keys()}")
