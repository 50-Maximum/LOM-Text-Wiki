# -*- coding: utf-8 -*-
"""盘点要改的地名：现有页面、上级、下辖、被引用次数。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

names = ["千金方医馆", "风雨山", "锦香宫", "峨眉山", "峨嵋山", "眉山", "丐帮-大义分舵",
         "华音阁", "江陵", "岳阳", "川蜀", "蜀中", "唐门", "崆峒山", "青城山"]
for nm in names:
    r = c.execute("select slug,lead,infobox,sections from pages where type='地点' and name=?",
                  (nm,)).fetchone()
    if not r:
        print("%-12s （无地点页）" % nm)
        continue
    inf = json.loads(r[2] or "{}")
    kids = []
    for s in json.loads(r[3] or "[]"):
        if s.get("h", "").startswith("下辖"):
            kids = [x.get("note", "").split("｜")[0] for x in (s.get("rows") or [])]
    print("%-12s 上级=%-10s 子=%d %s" % (nm, inf.get("上级"), len(kids), kids[:6]))

print("\n=== parent 表里现有")
par = json.load(open(B + r"\data\places_fix.json", encoding="utf-8")).get("parent", {})
for k, v in par.items():
    if k in names or v in names:
        print("  %-14s → %s" % (k, v))
print("  parent 共", len(par))
