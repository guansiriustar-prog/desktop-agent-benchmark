"""Summarise the latest WorkBuddy session: tool calls, names, and time span."""
import glob, json, os, sys
from datetime import datetime
files = sorted(glob.glob(os.path.expanduser("~/.workbuddy/projects/*/*.jsonl")), key=os.path.getmtime)
f = sys.argv[1] if len(sys.argv) > 1 else files[-1]
rows = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
def ts(r):
    t = r.get("timestamp")
    if isinstance(t, (int, float)):
        return datetime.fromtimestamp(t / 1000 if t > 1e12 else t)
    try:
        return datetime.fromisoformat(str(t).replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
    except Exception:
        return None
calls = [r for r in rows if r.get("type") == "function_call"]
msgs = [r for r in rows if r.get("type") == "message"]
print("file:", f)
user = [m for m in msgs if m.get("role") == "user"]
if user:
    c = user[0].get("content")
    txt = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
    print("user:", txt[:120])
stamps = [ts(r) for r in rows if ts(r)]
if stamps:
    print("span:", stamps[0].strftime("%H:%M:%S"), "->", stamps[-1].strftime("%H:%M:%S"), f"({(stamps[-1]-stamps[0]).total_seconds():.0f}s)")
print("tool calls:", len(calls))
for r in calls:
    args = r.get("arguments")
    a = args if isinstance(args, str) else json.dumps(args, ensure_ascii=False)
    print("  -", r.get("name"), "|", a.replace("\n", " ")[:150])

sub = glob.glob(os.path.join(f[:-len(".jsonl")], "subagents", "*.jsonl"))
subcalls = 0
for sf in sub:
    for l in open(sf, encoding="utf-8"):
        if l.strip() and json.loads(l).get("type") == "function_call":
            subcalls += 1
print("subagent calls:", subcalls, "| TOTAL steps:", len(calls) + subcalls)
