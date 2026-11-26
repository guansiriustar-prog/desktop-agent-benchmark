"""Wait until a file matching a glob exists and has not changed for a few seconds.
Usage: python3 -I wait_file.py '<glob>' [max_seconds]"""
import glob, os, sys, time
pat = os.path.expanduser(sys.argv[1])
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
t0 = time.time()
while time.time() - t0 < limit:
    hits = glob.glob(pat)
    if hits and all(time.time() - os.path.getmtime(h) > 4 for h in hits):
        print(f"FOUND after {int(time.time() - t0)}s:", hits)
        break
    time.sleep(2)
else:
    print("NOT FOUND within", limit, "s")
