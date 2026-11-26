"""Follow 豆包's runtime log and return when tool calls stop for a while.
Usage: python3 -I wait_db.py [max_seconds] [idle_seconds]
Prints the tool calls seen while waiting, then IDLE / TIMEOUT."""
import glob, os, re, sys, time
limit = float(sys.argv[1]) if len(sys.argv) > 1 else 100
idle = float(sys.argv[2]) if len(sys.argv) > 2 else 25
lg = max(glob.glob(os.path.expanduser("~/Library/Application Support/Doubao/sdk_storage/log/saman_2*.log")), key=os.path.getmtime)
fh = open(lg, "rb"); fh.seek(0, 2)
t0 = last = time.time(); n = 0
while time.time() - t0 < limit:
    chunk = fh.read()
    if chunk:
        for line in chunk.split(b"\n"):
            if b"ValidateSignedRequestForToolWithToolCallId: begin" in line:
                m = re.search(rb"tool=([\w.]+)", line)
                n += 1; last = time.time()
                print(time.strftime("%H:%M:%S"), m.group(1).decode() if m else "?", flush=True)
    if n and time.time() - last > idle:
        print(f"IDLE {int(time.time() - last)}s after {n} calls ({int(time.time() - t0)}s)"); break
    time.sleep(2)
else:
    print(f"TIMEOUT {int(limit)}s, {n} calls, last {int(time.time() - last)}s ago")
