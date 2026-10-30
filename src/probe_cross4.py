# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for kw in ["江陵事变", "赵活禀报大师兄行刺金人", "唐门商议应对飞石帮", "赵活向郁竹求婚"]:
    r = c.execute("select name,sections,infobox from pages where type='事件' and name like ?", ("%" + kw + "%",)).fetchone()
    if not r:
        print(kw, "无页")
        continue
    print("==", r["name"], json.loads(r["infobox"] or "{}").get("出现阶段", ""))
    for s in json.loads(r["sections"] or "[]"):
        h = s.get("h") or ""
        if h in ("触发条件",) or h.startswith("剧情") or h in ("分支选项",):
            continue
        for rw in (s.get("rows") or [])[:3]:
            print("   [%s] %s | %s" % (h, (rw.get("note") or "")[:60], rw.get("script")))
