# -*- coding: utf-8 -*-
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
print("== S2002 前缀的进入条件 ==")
for t, in c.execute("select name from sqlite_master where type='table'"):
    pass
try:
    for r in c.execute("select src,dst,cond,fn from scene_edges where dst like 'S2002%' or src like 'S2002%' limit 15"):
        print("   %s → %s | %s | %s" % (r["src"], r["dst"], (r["cond"] or "")[:60], r["fn"]))
except Exception as e:
    print("  edges 读失败", e)
sf = json.load(open(os.path.join(B, "scene_flags.json"), encoding="utf-8"))
for k, v in sf.items():
    if k.startswith("S2002"):
        print("   [flags] %s %s" % (k, json.dumps(v, ensure_ascii=False)[:160]))
print("\n== 东瀛 / 上官萤 旗标 ==")
for r in c.execute("select name from flaginfo limit 5"):
    pass
try:
    for r in c.execute("select script,seq,speaker,text from lines where text like '%东瀛%' limit 8"):
        print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"], (r["text"] or "")[:80]))
except Exception as e:
    print(" ", e)
