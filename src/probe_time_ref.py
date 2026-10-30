# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
n = c.execute("select count(*) from pages where type='场景' and infobox like '%据攻略年表%'").fetchone()[0]
tot = c.execute("select count(*) from pages where type='场景'").fetchone()[0]
n2 = c.execute("select count(*) from pages where type='事件' and infobox like '%据攻略年表%'").fetchone()[0]
print("场景带年表时间 %d / %d；事件 %d" % (n, tot, n2))
for slug in ("场景/ch1_1", "场景/S0003_02_01", "事件/赵活街头遇跪求药人"):
    r = c.execute("select name,infobox from pages where slug=?", (slug,)).fetchone()
    if r:
        inf = json.loads(r[1])
        print("  %-28s %s" % (slug, {k: inf[k] for k in ("时间", "阶段") if k in inf}))
