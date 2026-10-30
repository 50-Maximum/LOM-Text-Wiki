# -*- coding: utf-8 -*-
"""找可用的地点数据源：攻略索引/事件表、story 目录、mod 判定库里的地点条件。"""
import io, sys, os, re, json, sqlite3, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()

print("=== guide_index 列与样例")
print([d[1] for d in c.execute("pragma table_info(guide_index)")])
for r in c.execute("select * from guide_index limit 3"):
    print("  ", [str(x)[:40] for x in r])

print("\n=== guide_events 样例")
for r in c.execute("select * from guide_events limit 3"):
    print("  ", [str(x)[:50] for x in r])

print("\n=== story 目录文件")
for f in sorted(glob.glob(os.path.join(B, "data", "raw", "story", "*")))[:8]:
    print("  ", os.path.basename(f), os.path.getsize(f))
    head = open(f, encoding="utf-8", errors="replace").read()[:300].replace("\n", " ")
    print("      ", head[:200])

print("\n=== 场景 place 为空但脚本 id 有章号前缀的分布")
for pre, n in c.execute("""select substr(script,1,instr(script,'_')-1) p, count(*) from scenes
                           where coalesce(place,'')='' group by p order by 2 desc limit 15"""):
    print("  %-12s %d" % (pre, n))
