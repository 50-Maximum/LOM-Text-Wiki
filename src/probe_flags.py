# -*- coding: utf-8 -*-
"""追旗标置位点：G10001（认识上官萤）、E12001 等。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
sf = json.load(open(os.path.join(B, "scene_flags.json"), encoding="utf-8"))
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
ch = {r["script"]: (r["chapter"] or "") for r in c.execute("select script,chapter from scenes")}
ti = {r["script"]: (r["title"] or "") for r in c.execute("select script,title from scenes")}
for flag in ["G10001", "E12001", "M50017", "M10014"]:
    print("== %s 被设置的场景 ==" % flag)
    for sc, v in sf.items():
        sets = v.get("sets") or {}
        if flag in sets:
            print("   %-26s 章=%-6s %s  (置 %s)" % (sc, ch.get(sc, "-"), ti.get(sc, "")[:18], sets[flag]))
