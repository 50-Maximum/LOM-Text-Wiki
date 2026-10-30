# -*- coding: utf-8 -*-
"""应用势力细分结果：地点下沉、人群剔除、别名合并、重建 factions。"""
import sqlite3, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")
kinds = json.load(open(r"D:\LegendOfMortal Wiki\data\org_kinds.json", encoding="utf-8"))

# 人工裁定：其他类里哪些其实是组织
OVERRIDE = {"千灯楼": "组织", "吕氏商会": "组织", "养龙苑": "地点", "耕阳读书斋": "地点",
            "耕阳读书斋": "地点", "锦香宫": "门派", "松烟阁": "地点"}

def merge_entity(old_name, new_name, old_type="势力", new_type="势力"):
    if old_name == new_name:
        if old_type == new_type:
            return
        c.execute("update ledger set type=? where type=? and name=?", (new_type, old_type, old_name))
        cur = c.execute("select intro,aliases,tags,mentions,chapters,first_chapter from entities "
                        "where type=? and name=?", (new_type, old_name)).fetchone()
        src = c.execute("select intro,aliases,tags,mentions,chapters,first_chapter from entities "
                        "where type=? and name=?", (old_type, old_name)).fetchone()
        if src:
            if cur:
                intro = cur[0] if len(cur[0] or "") >= len(src[0] or "") else src[0]
                chs = sorted(set(json.loads(cur[4] or "[]")) | set(json.loads(src[4] or "[]")))
                c.execute("update entities set intro=?,mentions=?,chapters=? where type=? and name=?",
                          (intro, (cur[3] or 0) + (src[3] or 0),
                           json.dumps(chs, ensure_ascii=False), new_type, old_name))
            else:
                c.execute("insert or replace into entities(type,name,intro,aliases,tags,mentions,chapters,first_chapter)"
                          " values(?,?,?,?,?,?,?,?)", (new_type, old_name) + src)
            c.execute("delete from entities where type=? and name=?", (old_type, old_name))
        return
    rows = c.execute("select rowid,chapter,note from ledger where type=? and name=?",
                     (old_type, old_name)).fetchall()
    for rid, ch, note in rows:
        dup = c.execute("select 1 from ledger where chapter=? and type=? and name=? and note=?",
                        (ch, new_type, new_name, note)).fetchone()
        if dup:
            c.execute("delete from ledger where rowid=?", (rid,))
        else:
            c.execute("update ledger set type=?,name=? where rowid=?", (new_type, new_name, rid))
    for r in c.execute("select rowid,name from ledger where type='关系' and name like ?",
                       ("%" + old_name + "%",)).fetchall():
        c.execute("update ledger set name=? where rowid=?",
                  (r[1].replace(old_name, new_name), r[0]))
    src = c.execute("select intro,aliases,tags,mentions,chapters,first_chapter from entities "
                    "where type=? and name=?", (old_type, old_name)).fetchone()
    dst = c.execute("select intro,aliases,tags,mentions,chapters,first_chapter from entities "
                    "where type=? and name=?", (new_type, new_name)).fetchone()
    if src and dst:
        intro = dst[0] if len(dst[0] or "") >= len(src[0] or "") else src[0]
        al = sorted(set(json.loads(dst[1] or "[]")) | set(json.loads(src[1] or "[]")))
        tg = sorted(set(json.loads(dst[2] or "[]")) | set(json.loads(src[2] or "[]")))
        chs = sorted(set(json.loads(dst[4] or "[]")) | set(json.loads(src[4] or "[]")))
        c.execute("update entities set intro=?,aliases=?,tags=?,mentions=?,chapters=? "
                  "where type=? and name=?",
                  (intro, json.dumps(al, ensure_ascii=False), json.dumps(tg, ensure_ascii=False),
                   (dst[3] or 0) + (src[3] or 0), json.dumps(chs, ensure_ascii=False),
                   new_type, new_name))
        c.execute("delete from entities where type=? and name=?", (old_type, old_name))
    elif src:
        c.execute("insert or replace into entities(type,name,intro,aliases,tags,mentions,chapters,first_chapter)"
                  " values(?,?,?,?,?,?,?,?)", (new_type, new_name) + src)
        c.execute("delete from entities where type=? and name=?", (old_type, old_name))

stats = {"地点": 0, "人群": 0, "合并": 0}
for name, (kind, canonical, why) in kinds.items():
    k = OVERRIDE.get(name, kind)
    if k == "地点":
        merge_entity(name, name, "势力", "地点")
        stats["地点"] += 1
    elif k == "人群":
        c.execute("delete from ledger where type='势力' and name=?", (name,))
        c.execute("delete from entities where type='势力' and name=?", (name,))
        stats["人群"] += 1
    elif canonical != name:
        merge_entity(name, canonical)
        stats["合并"] += 1

# 重建 factions：只保留 门派/帮会/教派/世家/联盟/政权/军队/组织
KIND_OK = {"门派", "帮会", "教派", "世家", "联盟", "政权", "军队", "组织"}
c.execute("delete from factions")
rows = c.execute("select name from entities where type='势力'").fetchall()
added = 0
for (name,) in rows:
    k = None
    for old, (kk, canon, _) in kinds.items():
        if canon == name:
            k = OVERRIDE.get(old, kk)
            break
    if not k:
        k = OVERRIDE.get(name, "门派")
    if k not in KIND_OK:
        continue
    c.execute("insert or replace into factions(name,kind) values(?,?)", (name, k))
    added += 1

c.commit()
print("地点下沉", stats["地点"], "人群剔除", stats["人群"], "合并", stats["合并"])
print("factions", c.execute("select count(*) from factions").fetchone()[0])
print("势力实体", c.execute("select count(*) from entities where type='势力'").fetchone()[0],
      "地点实体", c.execute("select count(*) from entities where type='地点'").fetchone()[0])
for r in c.execute("select kind,count(*) from factions group by kind order by 2 desc"):
    print("   ", r[0], r[1])
