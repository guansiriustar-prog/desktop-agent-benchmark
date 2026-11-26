"""Wait until the newest 豆包 trajectory stops changing (the final answer is not written there).
Usage: python3 -I wait_dbt.py [max_seconds] [idle_seconds]"""
import glob, json, os, sys, time
limit = float(sys.argv[1]) if len(sys.argv) > 1 else 110
idle = float(sys.argv[2]) if len(sys.argv) > 2 else 25
base = os.path.expanduser("~/Library/Application Support/Doubao/Profile 3/.doubao/agent_mode/workspace/.sessions/")
t0 = time.time(); prev = -1
while time.time() - t0 < limit:
    f = max(glob.glob(base + "*/agents/*/system/trajectory.jsonl"), key=os.path.getmtime)
    n = 0
    for line in open(f, encoding="utf-8"):
        try: o = json.loads(line)
        except Exception: continue
        if o.get("role") == "assistant": n += len(o.get("tool_calls") or [])
    if n != prev: print(f"{time.strftime('%H:%M:%S')} tool calls: {n}", flush=True); prev = n
    quiet = time.time() - os.path.getmtime(f)
    if quiet > idle:
        print(f"QUIET {int(quiet)}s, {n} tool calls ({int(time.time()-t0)}s)"); break
    time.sleep(2)
else:
    print(f"TIMEOUT {int(limit)}s, {prev} tool calls")
