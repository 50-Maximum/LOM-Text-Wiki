# -*- coding: utf-8 -*-
"""清理台账：去泛称、去整章重复、归一名变体，建立 entities 汇总表。"""
import sqlite3, re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

# 1) 删除泛称/无信息条目
GENERIC = {
    "弟子", "众人", "那人", "此人", "有人", "旁人", "少年", "少女", "老者", "汉子",
    "掌柜", "店小二", "村民", "百姓", "士兵", "江湖人", "黑衣人", "陌生人", "路人",
    "老翁", "妇人", "男子", "女子", "小孩", "孩子", "客人", "掌柜的", "小二",
}
def is_generic(name, typ):
    if name in GENERIC:
        return True
    if typ == "人物":
        for g in ("弟子", "师兄", "师姐", "师弟", "师妹", "帮众", "教众", "门人"):
            if name.endswith(g) and len(name) <= 6:
                return True
    return False

rows = c.execute("select rowid,type,name from ledger").fetchall()
kill = [r[0] for r in rows if is_generic(r[2], r[1])]
c.executemany("delete from ledger where rowid=?", [(k,) for k in kill])
print("删除泛称", len(kill))

# 2) 整章条目去重：某章既有一整章标签又有分块标签时，整章行与分块行内容重复则删整章行
whole = {"第2章", "第3章", "第4章", "第5章", "第6章", "第7章", "第8章", "支线", "其他", "角色线"}
dup = 0
for ch in list(whole):
    has_parts = c.execute("select 1 from ledger where chapter like ? limit 1", (ch + "·%",)).fetchone()
    if not has_parts:
        continue
    rows = c.execute("select rowid,type,name,note from ledger where chapter=?", (ch,)).fetchall()
    for rid, typ, name, note in rows:
        hit = c.execute(
            "select 1 from ledger where chapter like ? and type=? and name=? and note=? limit 1",
            (ch + "·%", typ, name, note)).fetchone()
        if hit:
            c.execute("delete from ledger where rowid=?", (rid,))
            dup += 1
print("删除整章重复", dup)

# 3) 归一名变体
ALIAS = {
    "唐门弟子（师兄）": "唐门弟子",
}
for a, b in ALIAS.items():
    c.execute("update ledger set name=? where name=?", (b, a))

c.commit()
total = c.execute("select count(*) from ledger").fetchone()[0]
uniq = c.execute("select count(*) from (select distinct type,name from ledger)").fetchone()[0]
print("清理后", total, "行 /", uniq, "实体")
for t, n in c.execute("select type,count(distinct name) from ledger group by type order by 2 desc"):
    print(f"  {t} {n}")
