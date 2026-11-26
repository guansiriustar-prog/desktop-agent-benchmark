"""Summarise the latest 千问办公 session: tool calls, names, time span."""
import json, os, sqlite3, sys
from datetime import datetime
db = sqlite3.connect("file:" + os.path.expanduser("~/.qwenworkcn/.harness/flash-cli/qwenwork/qwenwork.db") + "?mode=ro", uri=True)
sid = sys.argv[1] if len(sys.argv) > 1 else db.execute("select id from session order by time_created desc limit 1").fetchone()[0]
title, created = db.execute("select title, time_created from session where id=?", (sid,)).fetchone()
parts = db.execute("select time_created, time_updated, data from part where session_id=? order by time_created", (sid,)).fetchall()
print("session:", sid, title)
if parts:
    t0, t1 = parts[0][0], max(p[1] for p in parts)
    f = lambda ms: datetime.fromtimestamp(ms / 1000).strftime("%H:%M:%S")
    print("span:", f(t0), "->", f(t1), f"({(t1 - t0) / 1000:.0f}s)")
tools = [json.loads(p[2]) for p in parts if json.loads(p[2]).get("type") == "tool"]
print("tool calls:", len(tools))
for d in tools:
    st = d.get("state", {})
    inp = json.dumps(st.get("input", {}), ensure_ascii=False).replace("\\n", " ")
    print("  -", d.get("tool"), st.get("status"), "|", inp[:150])
texts = [json.loads(p[2]).get("text", "") for p in parts if json.loads(p[2]).get("type") == "text"]
if texts:
    print("last text:", texts[-1].replace("\n", " ")[:300])
