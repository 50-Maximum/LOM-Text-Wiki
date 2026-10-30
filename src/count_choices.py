# -*- coding: utf-8 -*-
"""统计分支选项段落覆盖面。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for t in ("事件", "场景"):
    tot = c.execute("select count(*) from pages where type=?", (t,)).fetchone()[0]
    hit = c.execute("""select count(*) from pages where type=? and sections like '%"choice_rows"%'""",
                    (t,)).fetchone()[0]
    print("%s：%d / %d 带「分支选项」（%.0f%%）" % (t, hit, tot, 100.0 * hit / tot if tot else 0))
n = c.execute("""select count(*) from pages where sections like '%"choice_rows"%'""").fetchone()[0]
print("合计带分支选项的页面 %d" % n)
