# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db")
c.row_factory = sqlite3.Row

print("== 蝴蝶帮 覆灭相关原文 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%蝴蝶帮%' limit 25"):
    t = (r["text"] or "").replace("\n", "／")
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", t[:90]))

print("\n== 孤云山 提及 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%孤云山%' limit 10"):
    t = (r["text"] or "").replace("\n", "／")
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", t[:80]))

print("\n== 养龙苑 提及 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%养龙苑%' limit 8"):
    t = (r["text"] or "").replace("\n", "／")
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", t[:80]))

ff = json.load(open(B + r"\factions_fix.json", encoding="utf-8"))
print("\n== 现有 parent 表（含金国/养龙/华山/孤云） ==")
for k, v in sorted((ff.get("parent") or {}).items()):
    if k in ("养龙苑", "华山派", "孤云山", "孤云山派", "蝴蝶帮") or v in ("金国", "养龙苑"):
        print("   %s → %s" % (k, v))
