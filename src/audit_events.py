# -*- coding: utf-8 -*-
"""事件页体检：阶段与场景不符、跨阶段拼装、触发条件噪声。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
arcs = json.load(open(os.path.join(B, "arcs.json"), encoding="utf-8"))
ORDER = {a: i for i, a in enumerate(arcs["arcs"])}
arc_of_scene = {}
for r in c.execute("select script,chapter from scenes"):
    arc_of_scene[r["script"]] = None

# 页面里自带场景脚本；阶段用 arc 表重算太绕，这里只查「一页跨几个阶段」
rows = [r for r in c.execute("select name,facet,sections,infobox from pages where type='事件'")]
bad_noise, cross, stage_missing = [], [], []
for r in rows:
    try:
        secs = json.loads(r["sections"] or "[]")
        inf = json.loads(r["infobox"] or "{}")
    except Exception:
        continue
    st = inf.get("出现阶段") or ""
    sts = [x for x in st.split("、") if x]
    if len(sts) > 1:
        cross.append((r["name"], st))
    for s in secs:
        if s.get("h") == "触发条件":
            for rw in (s.get("rows") or []):
                n = rw.get("note") or ""
                if n.startswith("备注") or "差分" in n or "第三年" in n:
                    bad_noise.append((r["name"], n[:50]))
print("事件页 %d" % len(rows))
print("跨阶段拼装：%d 页" % len(cross))
print("触发条件噪声：%d 条" % len(bad_noise))
print("\n跨阶段样例：")
for n, st in cross[:15]:
    print("   %-24s %s" % (n, st))
print("\n噪声样例：")
for n, t in bad_noise[:10]:
    print("   %-24s %s" % (n, t))
