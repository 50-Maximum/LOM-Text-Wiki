# -*- coding: utf-8 -*-
"""第 5 批部署后核验：地名归一后，场景与地点页是否互相挂上。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row


def show(slug):
    r = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print(slug, "缺页")
        return
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            print("%-22s %s" % (slug, s["html"][:110]))


for sc in ("section_01_free_03_01", "S2600_02_03_01", "S2901_04_01", "craft_work_505", "ch2_5_2_3"):
    show("场景/" + sc)

print()
for pl in ("地点/崆峒-铁拳巷", "地点/崆峒-夺魄森林", "地点/崆峒-镇魂狱"):
    r = c.execute("select sections from pages where slug=?", (pl,)).fetchone()
    if not r:
        print(pl, "缺页")
        continue
    names = []
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") in ("发生场景", "出场场景"):
            names += [x.get("note") or x.get("title") for x in (s.get("rows") or [])]
    print("%-20s %s 条：%s" % (pl, len(names), "、".join(str(x)[:14] for x in names[:6])))
