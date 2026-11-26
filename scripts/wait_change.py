"""Wait until a file's mtime changes from its current value and then stays put for a few seconds.
Usage: python3 -I wait_change.py <path> [max_seconds] [settle_seconds]"""
import os, sys, time
p = os.path.expanduser(sys.argv[1])
limit = float(sys.argv[2]) if len(sys.argv) > 2 else 100
settle = float(sys.argv[3]) if len(sys.argv) > 3 else 6
m0 = os.path.getmtime(p) if os.path.exists(p) else None
t0 = time.time()
while time.time() - t0 < limit:
    m = os.path.getmtime(p) if os.path.exists(p) else None
    if m != m0 and m is not None and time.time() - m > settle:
        print(f"CHANGED, settled after {int(time.time() - t0)}s")
        break
    time.sleep(2)
else:
    print("NO CHANGE within", limit, "s")
