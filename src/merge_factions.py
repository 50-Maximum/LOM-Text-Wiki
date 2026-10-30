# -*- coding: utf-8 -*-
"""应用类型纠正与门派别名合并。"""
import sqlite3, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

# 1) 类型纠正：地点 → 势力（笔记主体是组织）
TYPE_FIX = [("地点", "唐门", "势力"), ("地点", "峨嵋", "势力"), ("地点", "崆峒", "势力"),
            ("地点", "点苍", "势力"), ("地点", "青城", "势力"), ("地点", "青城派", "势力")]

# 2) 别名归一（把左列并入右列）
ALIAS = {
    "峨嵋": "峨嵋派", "崆峒": "崆峒派", "点苍": "点苍派", "青城": "青城派",
    "全真教": "全真派", "崆峒四门": "崆峒派", "崆峒夺魄门": "夺魄门",
    "铁掌门": "铁拳门", "千灯教": "千灯楼",
}
# 门派表里其实是地点的，踢出去
DROP_FACTION = ["青城山", "崆峒山", "风雨山", "正心堂"]


def merge(old_type, old_name, new_type, new_name):
    if (old_type, old_name) == (new_type, new_name):
        return 0
    rows = c.execute("select rowid,chapter,note,evidence from ledger where type=? and name=?",
                     (old_type, old_name)).fetchall()
    moved = 0
    for rid, ch, note, ev in rows:
        dup = c.execute("select 1 from ledger where chapter=? and type=? and name=? and note=?",
                        (ch, new_type, new_name, note)).fetchone()
        if dup:
            c.execute("delete from ledger where rowid=?", (rid,))
        else:
            c.execute("update ledger set type=?, name=? where rowid=?", (new_type, new_name, rid))
            moved += 1
    # 关系名同步
    for r in c.execute("select rowid,name from ledger where type='关系' and name like ?",
                       ("%" + old_name + "%",)).fetchall():
        nn = r[1].replace(old_name, new_name)
        c.execute("update ledger set name=? where rowid=?", (nn, r[0]))
    # 实体合并
    src = c.execute("select intro,aliases,tags,mentions,chapters,first_chapter from entities "
                    "where type=? and name=?", (old_type, old_name)).fetchone()
    dst = c.execute("select intro,aliases,tags,mentions,chapters,first_chapter from entities "
                    "where type=? and name=?", (new_type, new_name)).fetchone()
    if src:
        if dst:
            intro = dst[0] if len(dst[0] or "") >= len(src[0] or "") else src[0]
            al = sorted(set(json.loads(dst[1] or "[]")) | set(json.loads(src[1] or "[]")))
            tg = sorted(set(json.loads(dst[2] or "[]")) | set(json.loads(src[2] or "[]")))
            chs = sorted(set(json.loads(dst[4] or "[]")) | set(json.loads(src[4] or "[]")))
            c.execute("update entities set intro=?,aliases=?,tags=?,mentions=?,chapters=? "
                      "where type=? and name=?",
                      (intro, json.dumps(al, ensure_ascii=False),
                       json.dumps(tg, ensure_ascii=False),
                       (dst[3] or 0) + (src[3] or 0),
                       json.dumps(chs, ensure_ascii=False), new_type, new_name))
        else:
            c.execute("insert or replace into entities(type,name,intro,aliases,tags,mentions,chapters,first_chapter) "
                      "values(?,?,?,?,?,?,?,?)", (new_type, new_name) + src)
        c.execute("delete from entities where type=? and name=?", (old_type, old_name))
    # 归属表
    c.execute("update char_faction set faction=? where faction=?", (new_name, old_name))
    if c.execute("select 1 from factions where name=?", (new_name,)).fetchone():
        c.execute("delete from factions where name=?", (old_name,))
    else:
        c.execute("update factions set name=? where name=?", (new_name, old_name))
    return moved


for d in DROP_FACTION:
    c.execute("delete from factions where name=?", (d,))
print("剔除非门派", len(DROP_FACTION))

total = 0
for ot, on, nt in TYPE_FIX:
    n = merge(ot, on, nt, on)
    total += n
    print(f"改类型 {on}: {ot} → {nt}，迁移 {n} 条")

for a, b in ALIAS.items():
    n = merge("势力", a, "势力", b)
    if n or a in ("峨嵋", "崆峒", "点苍", "青城"):
        print(f"合并 {a} → {b}，迁移 {n} 条")
    total += n

# 重建计数
c.execute("""update entities set mentions=(select count(*) from ledger l
             where l.type=entities.type and l.name=entities.name)""")
c.commit()
print()
print("总迁移", total)
print("势力", c.execute("select count(*) from entities where type='势力'").fetchone()[0],
      "地点", c.execute("select count(*) from entities where type='地点'").fetchone()[0])
print("势力表", c.execute("select count(*) from factions").fetchone()[0])
for r in c.execute("select name,kind from factions order by name"):
    print("   ", r[0], r[1])
