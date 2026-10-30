# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== ch6_5_1 叶辰相关 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%叶辰%' order by script,seq"):
    t = (r["text"] or "").replace("\n", "／")
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", t[:90]))
print("\n== 铁拳弟子 / 全胜利 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%铁拳弟子%' and text like '%火炎山%' limit 5"):
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "").replace("\n", "／")[:90]))
print("\n== 夏侯梅 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%夏侯梅%' limit 3"):
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "").replace("\n", "／")[:80]))
print("\n== 现有页名核对 ==")
for nm in ["皮康", "许亚霆", "瑞笙", "万里鹏程", "夏侯梅", "铁拳弟子", "叶辰", "全胜利"]:
    rows = [x["name"] for x in c.execute("select name from pages where type='人物' and name like ?", ("%" + nm,))]
    print("   %-6s %s" % (nm, rows))
