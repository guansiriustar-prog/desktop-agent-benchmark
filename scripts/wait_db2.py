"""Tail the newest 豆包 saman log and report sandbox tool calls + GUI executions until idle.
Usage: python3 -I wait_db2.py [max_seconds] [idle_seconds]"""
import glob, os, re, sys, time
limit = float(sys.argv[1]) if len(sys.argv) > 1 else 100
idle = float(sys.argv[2]) if len(sys.argv) > 2 else 40
lg = max(glob.glob(os.path.expanduser("~/Library/Application Support/Doubao/sdk_storage/log/saman_2*.log")), key=os.path.getmtime)
fh = open(lg, "rb"); fh.seek(0, 2)
t0 = last = time.time(); n = 0; buf = b""
while time.time() - t0 < limit:
    chunk = fh.read()
    if chunk:
        buf += chunk
        *lines, buf = buf.split(b"\n")
        for line in lines:
            m = re.match(rb"^\[\d+:\d+:\d{4}/(\d{6})\.\d+:[^\]]*\] (.*)", line)
            if not m: continue
            ts, rest = m.group(1).decode(), m.group(2)
            ev = None
            if b"ValidateSignedRequestForToolWithToolCallId: begin" in rest:
                t = re.search(rb"tool=([\w.]+)", rest); ev = t.group(1).decode() if t else "tool"
            elif rest.startswith(b"[gcu] execution finished"):
                ev = "GUI"
            elif b"local-file-ask-human" in rest and b"PushNotification return" in rest:
                ev = "ASK-HUMAN"
            if ev:
                n += 1; last = time.time(); print(f"{ts[:2]}:{ts[2:4]}:{ts[4:]} {ev}", flush=True)
    if time.time() - last > idle:
        print(f"IDLE {int(time.time()-last)}s after {n} events ({int(time.time()-t0)}s)"); break
    time.sleep(1.5)
else:
    print(f"TIMEOUT {int(limit)}s, {n} events, last {int(time.time()-last)}s ago")
