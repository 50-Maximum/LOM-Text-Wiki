# -*- coding: utf-8 -*-
"""看事件页现在有没有「触发条件」，以及条件文本可读性。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for name in ["南宫远就任武林盟主", "福韫", "小竹回家"]:
    r = c.execute("select slug,name,sections,infobox from pages where type='事件' and name like ?",
                  ("%" + name + "%",)).fetchone()
    if not r:
        print("\n", name, "无条目"); continue
    print("\n==", r["slug"], r["name"])
    for s in json.loads(r["sections"] or "[]"):
        h = s.get("h")
        if h in ("触发条件", "条件", "本场判定", "触发与条件"):
            print("  [%s]" % h)
            for x in (s.get("rows") or [])[:5]:
                print("     ", (x.get("note") or "")[:100])
    heads = [s.get("h") for s in json.loads(r["sections"] or "[]")]
    print("   栏目:", heads)
