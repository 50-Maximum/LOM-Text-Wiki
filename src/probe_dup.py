# -*- coding: utf-8 -*-
"""扫重复：同一页里同一目标在多个段/链接组重复出现。"""
import sqlite3, json, io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

dups = []
for slug, secs in c.execute("select slug,sections from pages where type in ('地点','势力')"):
    sec = json.loads(secs or "[]")
    names = [x["title"] for s in sec if s["h"].startswith("下辖") for x in (s.get("rows") or [])]
    if len(names) != len(set(names)):
        dups.append((slug, names))
print("下辖段内重复：", len(dups))
for d in dups[:10]:
    print(d)

# 链接本身重复
print("\n链接重复（同 页/目标/类型 出现两次）：")
cnt = c.execute("""select src,dst,kind,count(*) n from links group by src,dst,kind having n>1 limit 10""").fetchall()
print(cnt)

# 上下级链接是否还有
print("\n上级/下级 链接数：", c.execute("select kind,count(*) from links where kind in ('上级','下级') group by kind").fetchall())
