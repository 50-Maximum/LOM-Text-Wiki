# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for n in ("千金方医馆", "锦香宫", "华音阁", "峨嵋山", "岳阳", "川蜀", "眉山", "江陵"):
    r = c.execute("select lead,infobox from pages where type='地点' and name=?", (n,)).fetchone()
    if not r:
        print("%-8s 无页" % n)
        continue
    inf = json.loads(r[1] or "{}")
    print("%-8s 上级=%-6s 下辖=%-5s | %s" % (n, inf.get("上级") or "-", inf.get("下辖") or "-",
                                            (r[0] or "")[:46]))
