# -*- coding: utf-8 -*-
"""验证：①事件页是否都有剧情衔接 ②旗标检索能命中多少条（复现前端过滤逻辑）。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

tot = c.execute("select count(*) from pages where type='事件'").fetchone()[0]
hit = c.execute("""select count(*) from pages where type='事件'
                   and sections like '%剧情衔接%'""").fetchone()[0]
br = c.execute("""select count(*) from pages where type='事件'
                  and sections like '%分支选项%'""").fetchone()[0]
dm = c.execute("""select count(*) from pages where sections like '%梦境提示%'""").fetchone()[0]
print("事件页 %d ｜ 带剧情衔接 %d（%.0f%%）｜ 带分支选项 %d ｜ 梦境提示 %d"
      % (tot, hit, 100.0 * hit / tot if tot else 0, br, dm))

FL = json.load(open(r"D:\LegendOfMortal Wiki\web\flags.json", encoding="utf-8"))
for q in ("TC0001", "switch_001", "A00001"):
    fq = q.lower()
    hits = [x for x in FL if fq in x["f"].lower() or str(x["v"]) == q]
    print("\n搜索「%s」→ %d 条旗标命中，前 3：" % (q, len(hits)))
    for x in hits[:3]:
        print("   旗标 %s = %s ｜ %s ｜ %s" % (x["f"], x["v"], x["t"][:20], x["s"]))
