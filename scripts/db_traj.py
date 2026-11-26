"""List tool calls in the newest 豆包 session trajectory (or a given session id).
Usage: python3 -I db_traj.py [session_id]"""
import glob, json, os, sys
base = os.path.expanduser("~/Library/Application Support/Doubao/Profile 3/.doubao/agent_mode/workspace/.sessions/")
if len(sys.argv) > 1:
    fs = glob.glob(base + sys.argv[1] + "/agents/*/system/trajectory.jsonl")
else:
    fs = glob.glob(base + "*/agents/*/system/trajectory.jsonl")
f = max(fs, key=os.path.getmtime)
print(f.replace(base, ""))
n = 0; names = {}; final = ""
for line in open(f, encoding="utf-8"):
    try: o = json.loads(line)
    except Exception: continue
    if o.get("role") == "assistant":
        tcs = o.get("tool_calls") or []
        for tc in tcs:
            fn = tc.get("function", {}); nm = fn.get("name")
            if nm == "execute_defer_tool":
                nm = "gcu:" + str((fn.get("arguments") or {}).get("params", {}).get("title", ""))
            n += 1; names[nm.split(":")[0]] = names.get(nm.split(":")[0], 0) + 1
            print(n, nm, json.dumps(fn.get("arguments"), ensure_ascii=False)[:160])
        if o.get("content") and not tcs: final = str(o["content"])
print("TOTAL tool calls:", n, names)
print("FINAL:", final[:1500])
