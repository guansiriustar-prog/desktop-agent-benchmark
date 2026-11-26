"""Check the results of the office-document tasks in ~/Desktop/横评 against the clean originals.

Usage: python3 -I check.py T01 [T02 ...] | diff
Prints facts only; the judgement is made by reading the output.
"""
import hashlib
import io
import os
import subprocess
import sys
import zipfile
from xml.etree import ElementTree as ET

H = os.path.expanduser("~/Desktop/横评")
ORIG_ZIP = "../test-files/原件.zip"
THUMBS = "./thumbs"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"


def orig_bytes(name):
    with zipfile.ZipFile(ORIG_ZIP) as z:
        return z.read(name)


def docx_info(src):
    z = zipfile.ZipFile(src if not isinstance(src, bytes) else io.BytesIO(src))
    root = ET.fromstring(z.read("word/document.xml"))
    paras = ["".join(t.text or "" for t in p.iter(f"{{{W}}}t")) for p in root.iter(f"{{{W}}}p")]
    parts = [n for n in z.namelist() if n.startswith(("word/media/", "word/charts/", "word/embeddings/"))]
    charts = {}
    for n in parts:
        if n.startswith("word/charts/chart") and n.endswith(".xml"):
            croot = ET.fromstring(z.read(n))
            kinds = sorted({el.tag.split("}")[1] for el in croot.iter() if el.tag.endswith("Chart") and "}" in el.tag})
            vals = [v.text for v in croot.iter(f"{{{C}}}v")]
            charts[n] = {"kinds": kinds, "values": vals[:40]}
    return [p for p in paras if p.strip()], parts, charts


def xlsx_info(src):
    z = zipfile.ZipFile(src if not isinstance(src, bytes) else io.BytesIO(src))
    names = z.namelist()
    ss = []
    if "xl/sharedStrings.xml" in names:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall(f"{{{S}}}si"):
            ss.append("".join(t.text or "" for t in si.iter(f"{{{S}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    fills, xfs = [], []
    if "xl/styles.xml" in names:
        st = ET.fromstring(z.read("xl/styles.xml"))
        fe = st.find(f"{{{S}}}fills")
        for f in (fe if fe is not None else []):
            pf = f.find(f"{{{S}}}patternFill")
            desc = None
            if pf is not None and pf.get("patternType") not in (None, "none", "gray125"):
                fg = pf.find(f"{{{S}}}fgColor")
                if fg is not None:
                    desc = fg.get("rgb") or (f"indexed:{fg.get('indexed')}" if fg.get("indexed") else None) or \
                        (f"theme:{fg.get('theme')}/tint:{fg.get('tint')}" if fg.get("theme") else None)
                desc = desc or f"pattern:{pf.get('patternType')}"
            elif f.find(f"{{{S}}}gradientFill") is not None:
                desc = "gradient"
            fills.append(desc)
        cx = st.find(f"{{{S}}}cellXfs")
        for xf in (cx if cx is not None else []):
            xfs.append(int(xf.get("fillId", "0")))

    def fill_of(s):
        return fills[xfs[s]] if s < len(xfs) and xfs[s] < len(fills) else None

    out = {}
    for sh in wb.find(f"{{{S}}}sheets"):
        target = relmap[sh.get(f"{{{R}}}id")]
        target = target[1:] if target.startswith("/") else "xl/" + target
        root = ET.fromstring(z.read(target))
        cells, rowfill = {}, {}
        for row in root.iter(f"{{{S}}}row"):
            if row.get("customFormat") == "1" and row.get("s"):
                rowfill[int(row.get("r"))] = fill_of(int(row.get("s")))
        for c in root.iter(f"{{{S}}}c"):
            t, v, f = c.get("t"), c.find(f"{{{S}}}v"), c.find(f"{{{S}}}f")
            if t == "s" and v is not None:
                val = ss[int(v.text)]
            elif t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(f"{{{S}}}t"))
            else:
                val = v.text if v is not None else None
            cells[c.get("r")] = (val, f.text if f is not None else None, fill_of(int(c.get("s", "0"))))
        out[sh.get("name")] = {"cells": cells, "rowfill": rowfill}
    return out


def rows_of(sheet):
    rows = {}
    for ref, cell in sheet["cells"].items():
        col = "".join(ch for ch in ref if ch.isalpha())
        r = int("".join(ch for ch in ref if ch.isdigit()))
        rows.setdefault(r, {})[col] = cell
    return rows


def thumb(path):
    os.makedirs(THUMBS, exist_ok=True)
    subprocess.run(["qlmanage", "-t", "-s", "900", "-o", THUMBS, path], capture_output=True)
    p = os.path.join(THUMBS, os.path.basename(path) + ".png")
    return p if os.path.exists(p) else "(no thumbnail)"


def text_of(path):
    if path.lower().endswith(".txt"):
        return open(path, encoding="utf-8", errors="replace").read()
    r = subprocess.run(["textutil", "-convert", "txt", "-stdout", path], capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def diff():
    with zipfile.ZipFile(ORIG_ZIP) as z:
        orig = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
    now = {}
    for root, _, files in os.walk(H):
        for fn in files:
            if fn == ".DS_Store":
                continue
            full = os.path.join(root, fn)
            now[os.path.relpath(full, H)] = hashlib.sha256(open(full, "rb").read()).hexdigest()
    for n in sorted(set(orig) | set(now)):
        if n not in now:
            print("  missing :", n)
        elif n not in orig:
            print("  new     :", n)
        elif orig[n] != now[n]:
            print("  changed :", n)


def t01():
    new, _, _ = docx_info(os.path.join(H, "会议纪要.docx"))
    old, _, _ = docx_info(orig_bytes("会议纪要.docx"))
    print("  title now:", new[0] if new else None)
    print("  body unchanged:", new[1:] == old[1:])
    if new[1:] != old[1:]:
        print("  body now:", new[1:])


def t02():
    sh = next(iter(xlsx_info(os.path.join(H, "报销明细.xlsx")).values()))
    rows = rows_of(sh)
    orig = rows_of(next(iter(xlsx_info(orig_bytes("报销明细.xlsx")).values())))
    for r in sorted(rows):
        vals = [rows[r].get(c, (None,))[0] for c in "ABCDE"]
        fills = {c: rows[r][c][2] for c in rows[r] if rows[r][c][2]}
        same = r in orig and vals == [orig[r].get(c, (None,))[0] for c in "ABCDE"]
        print(f"  row {r}: {vals} fills={fills or '-'} rowfill={sh['rowfill'].get(r, '-')} same_as_orig={same}")
    extra = [c for r in rows for c in rows[r] if c not in "ABCDE"]
    print("  cells outside A:E:", extra or "none")


def t03():
    pdfs = [f for f in os.listdir(H) if f.lower().endswith(".pdf")]
    print("  pdfs:", pdfs)
    for f in pdfs:
        p = os.path.join(H, f)
        print("   ", f, os.path.getsize(p), "bytes, header", open(p, "rb").read(5), "thumb:", thumb(p))


def t04():
    hits = [f for f in os.listdir(H) if f.startswith("销售汇报")]
    print("  files:", hits)
    for f in hits:
        p = os.path.join(H, f)
        if f.endswith(".docx"):
            paras, parts, charts = docx_info(p)
            print("  paragraphs:", paras[:6])
            print("  media/charts:", parts)
            for n, info in charts.items():
                print("  chart", n, info)
        print("  thumb:", thumb(p))
    sales = xlsx_info(os.path.join(H, "销售数据.xlsx"))
    orig = rows_of(next(iter(xlsx_info(orig_bytes("销售数据.xlsx")).values())))
    for name, sh in sales.items():
        rows = rows_of(sh)
        same = all(rows.get(r, {}).get(c, (None,))[0] == orig[r][c][0] for r in orig for c in orig[r])
        print(f"  sheet {name}: data same as original = {same}")


def t05():
    book = xlsx_info(os.path.join(H, "通讯录.xlsx"))
    print("  sheets:", list(book))
    orig = rows_of(next(iter(xlsx_info(orig_bytes("通讯录.xlsx")).values())))
    for name, sh in book.items():
        rows = rows_of(sh)
        print(f"  [{name}] {len(rows)} rows")
        for r in sorted(rows):
            print("    ", r, [rows[r].get(c, (None,))[0] for c in "ABCD"])
        if name == "通讯录":
            same = all(rows.get(r, {}).get(c, (None,))[0] == orig[r][c][0] for r in orig for c in orig[r])
            print("   original data intact:", same)


def t10():
    hits = [f for f in os.listdir(H) if f.startswith("季度要点")]
    print("  files:", hits)
    for f in hits:
        t = text_of(os.path.join(H, f))
        print("  text:", t.strip()[:400])
        print("  has 1286:", "1286" in t, "| has 9 月:", any(k in t for k in ("9月", "9 月", "九月")), "| has 443:", "443" in t)


def t15():
    sh = next(iter(xlsx_info(os.path.join(H, "购物清单.xlsx")).values()))
    rows = rows_of(sh)
    for r in sorted(rows):
        print("  ", r, [rows[r].get(c, (None,))[0] for c in "ABCD"])


CHECKS = {"T01": t01, "T02": t02, "T03": t03, "T04": t04, "T05": t05, "T10": t10, "T15": t15}

for arg in sys.argv[1:]:
    print(f"== {arg}")
    if arg == "diff":
        diff()
    else:
        try:
            CHECKS[arg]()
        except Exception as e:  # report and keep going
            print("  ERROR:", type(e).__name__, e)
