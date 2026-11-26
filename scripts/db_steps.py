"""List 豆包 tool calls from its runtime log between two times (HHMMSS, today's log).
Usage: python3 -I db_steps.py 224152 224310 [MMDD]"""
import glob, os, re, sys
start, end = sys.argv[1], sys.argv[2]
mmdd = sys.argv[3] if len(sys.argv) > 3 else None
logs = sorted(glob.glob(os.path.expanduser("~/Library/Application Support/Doubao/sdk_storage/log/saman_2*.log")), key=os.path.getmtime)
pat = re.compile(rb"^\[\d+:\d+:(\d{4})/(\d{6})\.\d+:[^\]]*\] .*ValidateSignedRequestForToolWithToolCallId: begin tool=([\w.]+), request_id=\S+, (?:call_id|tool_call_id)?=?(\S*)")
seen, calls = set(), []
for lg in logs[-2:]:
    with open(lg, "rb") as fh:
        for line in fh:
            if b"ValidateSignedRequestForToolWithToolCallId: begin" not in line:
                continue
            m = re.match(rb"^\[\d+:\d+:(\d{4})/(\d{6})\.\d+:[^\]]*\] (.*)", line)
            if not m:
                continue
            d, t, rest = m.group(1).decode(), m.group(2).decode(), m.group(3).decode("utf-8", "replace")
            if mmdd and d != mmdd:
                continue
            if not (start <= t <= end):
                continue
            tool = re.search(r"tool=([\w.]+)", rest).group(1)
            cid = re.search(r"tool_call_id=([^,\s]+)", rest) or re.search(r"call_id=([^,\s]+)", rest)
            key = cid.group(1) if cid else rest
            if key in seen:
                continue
            seen.add(key)
            calls.append((t, tool, key[:24]))
for c in calls:
    print(*c)
print("TOTAL", len(calls))
