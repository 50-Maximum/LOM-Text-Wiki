# -*- coding: utf-8 -*-
"""核验条件条目、场景去向、ch8_8_1 地点。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row

print("条件条目:", con.execute("select count(*) from pages where type='条件'").fetchone()[0])
for cid in ["Ch_6_7_1_004", "Ch_6_7_1_005", "Ch_6_7_1_006", "M60015_01", "S_Beh_LT_60"]:
    r = con.execute("select name,lead,infobox,length(sections) L from pages where slug=?",
                    ("条件/" + cid,)).fetchone()
    print("  %-14s %s" % (cid, (r["lead"][:90] if r else "缺页")))
    if r:
        print("       ", r["infobox"], "| 章节长度", r["L"])

def page(sc):
    r = con.execute("select name,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        return "(无)"
    info = ""
    heads = []
    for s in json.loads(r["sections"] or "[]"):
        heads.append(s.get("h"))
        if s.get("h") == "场景信息":
            info = s.get("html") or ""
        if s.get("h") == "接下来":
            info += " ｜ 去向: " + " / ".join(x.get("note", "") for x in (s.get("rows") or [])[:4])
    return (r["name"] or "") + " ｜ " + info + " ｜ 栏目:" + ",".join(heads)

for sc in ["ch8_8_1", "ch6_7_1", "S0022_01"]:
    print("\n", sc, page(sc)[:520])
