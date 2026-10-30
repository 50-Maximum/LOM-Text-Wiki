# -*- coding: utf-8 -*-
"""speaker_id 是否就是脚本里的角色键（sister1 等），可用来做 id→中文名映射。"""
import io, sys, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = list(c.execute("""select speaker_id,speaker,count(*) n from lines
                         where speaker_id<>'' group by speaker_id order by n desc limit 12"""))
for sid, sp, n in rows:
    print("  %-14s → %-10s %d 句" % (sid, sp, n))
print("\n是否有 sister1：", c.execute(
    "select speaker,speaker_id from lines where speaker_id='sister1' limit 1").fetchone())
