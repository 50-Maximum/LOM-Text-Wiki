# -*- coding: utf-8 -*-
"""核对三处：青城山镇/都江客栈、锦香宫→岳阳、以及无上级地点数。"""
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

print("=== 名称匹配")
for kw in ("青城", "都江", "锦香", "岳阳"):
    for nm, up, fc in c.execute("""select name, json_extract(infobox,'$.上级'), facet
                                   from pages where type='地点' and name like ?""", ("%" + kw + "%",)):
        print("  %-16s 上级=%-12s facet=%s" % (nm, up or "-", fc or "（空）"))

print("\n=== parent 表里相关条目")
par = json.load(open(B + r"\data\places_fix.json", encoding="utf-8")).get("parent", {})
for k, v in par.items():
    if any(x in k or x in v for x in ("青城", "都江", "锦香", "岳阳")):
        print("  %-18s → %s" % (k, v))

print("\n=== 无上级地点数")
print(" ", c.execute("""select count(*) from pages where type='地点'
                       and (json_extract(infobox,'$.上级') is null
                            or json_extract(infobox,'$.上级')='')""").fetchone()[0])
