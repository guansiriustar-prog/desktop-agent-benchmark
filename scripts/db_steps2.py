"""Count 豆包 steps in a time window: sandbox tool calls (bash/fs) + GUI executions (gcu).
Usage: python3 -I db_steps2.py HHMMSS HHMMSS [MMDD]"""
import glob, os, re, sys, time
start, end = sys.argv[1], sys.argv[2]
mmdd = sys.argv[3] if len(sys.argv) > 3 else time.strftime("%m%d")
logs = sorted(glob.glob(os.path.expanduser("~/Library/Application Support/Doubao/sdk_storage/log/saman_2*.log")), key=os.path.getmtime)[-2:]
tools, gui, actions = [], [], {}
for lg in logs:
    with open(lg, "rb") as fh:
        for line in fh:
            m = re.match(rb"^\[\d+:\d+:(\d{4})/(\d{6})\.\d+:[^\]]*\] (.*)", line)
            if not m or m.group(1).decode() != mmdd or not (start <= m.group(2).decode() <= end):
                continue
            t, rest = m.group(2).decode(), m.group(3)
            if b"ValidateSignedRequestForToolWithToolCallId: begin" in rest:
                tools.append((t, re.search(rb"tool=([\w.]+)", rest).group(1).decode()))
            elif rest.startswith(b"[gcu] execution finished"):
                gui.append(t)
            else:
                a = re.search(rb"call_tool_async: method=(app\.[a-z_]+)", rest)
                if a:
                    actions[a.group(1).decode()] = actions.get(a.group(1).decode(), 0) + 1
print("sandbox tool calls:", len(tools), {k: sum(1 for _, x in tools if x == k) for k in sorted(set(x for _, x in tools))})
print("GUI executions:", len(gui), "| app.* calls:", actions)
print("TOTAL steps:", len(tools) + len(gui))
