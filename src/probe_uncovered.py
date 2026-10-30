# -*- coding: utf-8 -*-
import io, sys, sqlite3, json, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("select name,slug,sections from pages where slug like '事件/%' and sections not like '%触发条件%'").fetchall()
print("无触发条件事件:", len(rows))
pref = collections.Counter()
for nm, slug, sec in rows:
    sc = c.execute("select script from notes where type='事件' and name=? limit 1", (nm,)).fetchone()
    s = sc[0] if sc else "?"
    pref[re.sub(r"[\d_].*$", "", s) or "?"] += 1
print("脚本前缀分布:", pref.most_common(12))
print("\n样例:")
for nm, slug, sec in rows[:12]:
    sc = c.execute("select script from notes where type='事件' and name=? limit 1", (nm,)).fetchone()
    print("   %-22s %s" % (nm[:22], sc[0] if sc else "?"))
