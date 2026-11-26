"""Print the wallpaper settings (decoding the nested binary plists). Usage: python3 -I wp_show.py [Index.plist]"""
import plistlib, sys, os
p = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Library/Application Support/com.apple.wallpaper/Store/Index.plist")
d = plistlib.load(open(p, "rb"))
def dec(b):
    try:
        x = plistlib.loads(b)
    except Exception:
        return b
    return x
def show(name, sect):
    c = sect.get("Content", {})
    for ch in c.get("Choices", []):
        conf = dec(ch.get("Configuration", b""))
        print(f"  {name}: provider={ch.get('Provider')} conf={conf} files={ch.get('Files')}")
    ev = dec(c.get("EncodedOptionValues", b""))
    print(f"  {name}: options={ev} shuffle={c.get('Shuffle')} LastSet={sect.get('LastSet')}")
print("AllSpacesAndDisplays:", d.get("AllSpacesAndDisplays", {}).get("Type"))
for k in ("Desktop", "Idle", "Linked"):
    if k in d.get("AllSpacesAndDisplays", {}):
        show("All." + k, d["AllSpacesAndDisplays"][k])
for disp, v in d.get("Displays", {}).items():
    print("Display", disp, "type", v.get("Type"))
    for k in ("Desktop", "Idle", "Linked"):
        if k in v: show(k, v[k])
for sp, v in d.get("Spaces", {}).items():
    print("Space", sp, list(v.keys()) if isinstance(v, dict) else v)
print("top-level keys:", list(d.keys()))
for sp, v in d.get("Spaces", {}).items():
    print("== Space", repr(sp))
    dflt = v.get("Default", {})
    print("  Default type", dflt.get("Type"))
    for k in ("Desktop", "Idle", "Linked"):
        if k in dflt: show("Default." + k, dflt[k])
    for disp, dv in v.get("Displays", {}).items():
        print("  Display", disp, "type", dv.get("Type"))
        for k in ("Desktop", "Idle", "Linked"):
            if k in dv: show("  " + k, dv[k])
sd = d.get("SystemDefault", {})
print("== SystemDefault type", sd.get("Type"))
for k in ("Desktop", "Idle", "Linked"):
    if k in sd: show("SD." + k, sd[k])
