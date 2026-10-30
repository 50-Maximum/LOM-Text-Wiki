# -*- coding: utf-8 -*-
import io, sys, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== guide_events.cond 非空 ===")
for r in c.execute("select name,year,month,xun,place,cond from guide_events where cond is not null and trim(cond)<>'' limit 15"):
    print(" ", r[0], "|", f"{r[1]}年{r[2]}月{r[3]}", "|", r[4], "|", str(r[5])[:120])
print("\n=== guide_index body 前 130 字 ===")
for r in c.execute("select name,body from guide_index limit 18"):
    b = re.sub(r"\s+", " ", r[1] or "")
    print(" ¶", r[0], "::", b[:130])
print("\n=== 含 触发 的句子（前 80 条）===")
n = 0
for (nm, b) in c.execute("select name,body from guide_index"):
    b = re.sub(r"\s+", "", b or "")
    for m in re.finditer(r"触发[^|]{0,60}", b):
        s = m.group(0)
        if len(s) > 8:
            print("  ", nm, "->", s)
            n += 1
            break
    if n >= 25:
        break
