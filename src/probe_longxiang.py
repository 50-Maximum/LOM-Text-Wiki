# -*- coding: utf-8 -*-
"""找龙湘在卧云岗事件里的三个绰号（看该地场景的选项文本）。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
scenes = [r[0] for r in c.execute("select script from scenes where place like '%卧云岗%' or place like '%锦香%'")]
print("相关系列场景", len(scenes), scenes[:8])
seen = 0
for sc in scenes:
    for r in c.execute("select seq,speaker,text from lines where script=? and (text like '%号%' or text like '%称%' or text like '%名%') limit 6", (sc,)):
        t = r["text"] or ""
        if any(k in t for k in ("绰号", "称号", "外号", "人称", "封号", "名号")):
            print("   [%s#%d] %s：%s" % (sc, r["seq"], r["speaker"] or "-", t[:100]))
            seen += 1
            if seen > 20:
                sys.exit(0)
print("命中", seen)

print("\n== 选项文本里含「仙/侠/姬/娘」的 ==")
for r in c.execute("select script,seq,text from lines where kind='option' and (text like '%仙%' or text like '%侠%' or text like '%姬%') limit 15"):
    print("   [%s#%d] %s" % (r["script"], r["seq"], (r["text"] or "")[:70]))
