# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print([r[0] for r in c.execute("select name from sqlite_master where type='table' order by name")])
print("\n战斗角色相关 entries：")
for r in c.execute("""select eid,title,body from entries
                      where ns='CombatCharacter_zh-cn' limit 6"""):
    print("  ", r)
