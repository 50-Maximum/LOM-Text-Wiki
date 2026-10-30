# -*- coding: utf-8 -*-
"""查福建、剑门关、腾云寨、渡口的现状，准备第 8 批。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for nm in ("福建", "福州", "剑门关", "腾云寨", "腾云山", "渡口", "朱仙镇", "岳阳",
           "锦香宫", "唐门", "崆峒山", "上官交引舖", "栖霞太虚观", "烟花阁", "画舫",
           "野狐桥", "朱家葱肉包摊", "临镇"):
    rows = list(c.execute("select slug,type,facet,facet2,infobox from pages where name=?", (nm,)))
    if not rows:
        print("%-10s 无条目" % nm)
        continue
    for r in rows:
        inf = json.loads(r["infobox"] or "{}")
        print("%-10s %-22s %-4s 区域=%-6s 类型=%-6s 上级=%s"
              % (nm, r["slug"], r["type"], r["facet"], r["facet2"], inf.get("上级") or "-"))
