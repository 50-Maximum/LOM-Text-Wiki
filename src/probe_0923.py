# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for sc in ["S0014_01_01", "S0014_01_02", "S9001_01", "S9001_03", "S9001_04", "S0012_01_01",
           "S9904_01", "S9904_01_02", "act2_3", "talk_brother4_option_02_03"]:
    t = c.execute("select year,month,xun,event from scene_time where script=?", (sc,)).fetchone()
    print("==", sc, "| 时间:", (dict(t) if t else "无"))
    for r in c.execute("select type,name,note from notes where script=? and type='事件'", (sc,)):
        print("   [事件] %s :: %s" % (r["name"], (r["note"] or "")[:90]))
print("\n== 原始台词（S0014_01_01 / 02 点穴相关）==")
for sc in ["S0014_01_01", "S0014_01_02"]:
    for r in c.execute("select seq,speaker,text from lines where script=? and (text like '%穴%' or text like '%指点%' or text like '%前辈%') order by seq limit 8", (sc,)):
        print("  [%s#%d] %s：%s" % (sc, r["seq"], r["speaker"], (r["text"] or "").replace("\n", "／")[:90]))
