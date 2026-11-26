"""Wait until the agent finishes, goes idle (maybe waiting for a prompt), or time runs out.
Usage: python3 -I wait_agent.py wb|qw [max_seconds] [idle_seconds]"""
import glob, json, os, sqlite3, sys, time
mode = sys.argv[1]
maxwait = float(sys.argv[2]) if len(sys.argv) > 2 else 100
idle_limit = float(sys.argv[3]) if len(sys.argv) > 3 else 25

def wb():
    f = max(glob.glob(os.path.expanduser("~/.workbuddy/projects/*/*.jsonl")), key=os.path.getmtime)
    last = None
    for line in open(f, encoding="utf-8"):
        if line.strip():
            last = line
    r = json.loads(last) if last else {}
    done = r.get("type") == "message" and r.get("role") == "assistant"
    return done, os.path.getmtime(f), r.get("type")

def qw():
    p = os.path.expanduser("~/.qwenworkcn/.harness/flash-cli/qwenwork/qwenwork.db")
    db = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    sid = db.execute("select id from session order by time_created desc limit 1").fetchone()[0]
    row = db.execute("select data, time_updated from part where session_id=? order by time_created desc limit 1", (sid,)).fetchone()
    db.close()
    d = json.loads(row[0]) if row else {}
    mt = max(os.path.getmtime(x) for x in (p, p + "-wal") if os.path.exists(x))
    done = d.get("type") == "step-finish" and d.get("reason") == "stop"
    state = d.get("type") + (":" + str(d.get("state", {}).get("status")) if d.get("type") == "tool" else "")
    return done, mt, state

fn = wb if mode == "wb" else qw
t0 = time.time()
while True:
    try:
        done, mt, state = fn()
    except Exception as e:
        done, mt, state = False, time.time(), f"err {e}"
    now = time.time()
    if done and now - mt > 4:
        print(f"DONE after {now - t0:.0f}s (last={state})"); break
    if not done and now - mt > idle_limit:
        print(f"IDLE {now - mt:.0f}s (last={state}) after {now - t0:.0f}s"); break
    if now - t0 > maxwait:
        print(f"TIMEOUT {now - t0:.0f}s (last={state})"); break
    time.sleep(2)
