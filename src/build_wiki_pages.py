# -*- coding: utf-8 -*-
"""把实体/词条/场景整理成 wiki 页面：pages + links + redirects。

页面 slug 形如「人物/赵活」「势力/唐门」「场景/ch6_5_1」。
"""
import sqlite3, sys, io, json, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

c.executescript("""
DROP TABLE IF EXISTS pages;
DROP TABLE IF EXISTS links;
DROP TABLE IF EXISTS redirects;
CREATE TABLE pages(
  slug TEXT PRIMARY KEY, type TEXT, name TEXT, lead TEXT,
  infobox TEXT, sections TEXT, cats TEXT, mentions INT,
  chapters TEXT, sort_key TEXT
);
CREATE TABLE links(src TEXT, dst TEXT, kind TEXT, label TEXT);
CREATE TABLE redirects(alias TEXT PRIMARY KEY, slug TEXT);
CREATE INDEX idx_pages_type ON pages(type);
CREATE INDEX idx_links_dst ON links(dst);
CREATE INDEX idx_links_src ON links(src);
""")

# ---------- 章节排序 ----------
CH_ORDER = {"序章": 0, "第0章": 1, "第1章": 2}
def chap_key(ch):
    ch = (ch or "").strip()
    if ch in CH_ORDER:
        return (CH_ORDER[ch], 0)
    m = re.match(r"第(\d+)章", ch)
    if m:
        p = re.search(r"·(\d+)$", ch)
        return (10 + int(m.group(1)), int(p.group(1)) if p else 0)
    if ch.startswith("支线"):
        p = re.search(r"·(\d+)$", ch)
        return (100, int(p.group(1)) if p else 0)
    if ch == "角色线":
        return (200, 0)
    if ch.startswith("其他"):
        p = re.search(r"·(\d+)$", ch)
        return (300, int(p.group(1)) if p else 0)
    return (400, 0)

def ordered(notes):
    return sorted(notes, key=lambda x: chap_key(x["ch"] if isinstance(x, dict) else x[0]))

pages, links, redirects = [], [], []
def add_page(slug, typ, name, lead, infobox, sections, cats, mentions, chapters, sort_key=""):
    pages.append((slug, typ, name, lead or "", json.dumps(infobox, ensure_ascii=False),
                  json.dumps(sections, ensure_ascii=False), json.dumps(cats, ensure_ascii=False),
                  mentions, json.dumps(chapters, ensure_ascii=False), sort_key))

def add_link(src, dst, kind, label=""):
    links.append((src, dst, kind, label))

# ---------- 实体页 ----------
ents = c.execute("select type,name,intro,aliases,tags,mentions,chapters,faction,faction_ev "
                 "from entities").fetchall()
byname = {(t, n): (intro, al, tg, m, chs, fc, fce)
          for t, n, intro, al, tg, m, chs, fc, fce in
          [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]) for r in ents]}
name2slug = {}
for t, n, intro, al, tg, m, chs, fc, fce in ents:
    name2slug[(t, n)] = f"{t}/{n}"

def notes_of(typ, name):
    rows = c.execute("select chapter,note,evidence from ledger where type=? and name=? order by rowid",
                     (typ, name)).fetchall()
    seen, out = set(), []
    for ch, note, ev in rows:
        if note in seen:
            continue
        seen.add(note)
        out.append({"ch": ch, "text": note, "ev": ev or ""})
    return ordered(out)

for t, n, intro, al, tg, m, chs, fc, fce in ents:
    if t == "关系":
        continue
    slug = f"{t}/{n}"
    aliases = json.loads(al or "[]")
    tags = json.loads(tg or "[]")
    chapters = json.loads(chs or "[]")
    inf = {"类型": t}
    if aliases:
        inf["别称"] = "、".join(aliases)
    if tags:
        inf["标签"] = "、".join(tags)
    if fc:
        inf["归属"] = fc
    inf["提及"] = f"{m} 处"
    if chapters:
        inf["首见"] = chapters[0]
    secs = [{"h": "简介", "html": intro or "（暂无）"}]
    ns = notes_of(t, n)
    if len(ns) > 1:
        secs.append({"h": "原文脉络", "notes": ns})
    cats = [t] + ([fc] if fc else []) + chapters[:6]
    add_page(slug, t, n, intro or "", inf, secs, cats, m, chapters)
    for a in aliases:
        if a and a != n:
            redirects.append((a, slug))

# ---------- 关系 → 链接 ----------
for name, note, ch in c.execute("select name,note,chapter from ledger where type='关系'").fetchall():
    parts = [p.strip() for p in re.split("[—－-]", name) if p.strip()]
    if len(parts) != 2:
        continue
    a, b = parts
    sa = next((f"{t}/{a}" for (t, x) in name2slug if x == a), None)
    sb = next((f"{t}/{b}" for (t, x) in name2slug if x == b), None)
    if sa and sb:
        add_link(sa, sb, "关系", note)
        add_link(sb, sa, "关系", note)

# ---------- 势力成员 ----------
for name, fac in c.execute("select name,faction from entities where type='人物' and faction<>''"):
    ps = f"人物/{name}"
    fs = f"势力/{fac}"
    if (fac,) in [(r[0],) for r in c.execute("select name from entities where type='势力'")]:
        add_link(ps, fs, "归属", "")
        add_link(fs, ps, "成员", "")

# ---------- 地点父子 ----------
places = [r[0] for r in c.execute("select name from entities where type='地点'")]
pset = set(places)
for p in places:
    if "-" in p:
        root = p.split("-")[0]
        if root in pset:
            add_link(f"地点/{p}", f"地点/{root}", "上级", "")
            add_link(f"地点/{root}", f"地点/{p}", "下级", "")

# ---------- 场景页 ----------
scenes = c.execute("""select script,title,chapter,place,line_count,cjk,time_from,time_to,battles
                      from scenes where line_count>0""").fetchall()
for script, title, ch, place, lc, cjk, tf, tt, bt in scenes:
    slug = f"场景/{script}"
    inf = {"脚本": script, "章节": ch, "句数": lc}
    if place:
        inf["地点"] = place
    if tf or tt:
        inf["时间"] = (tf or "") + (" ~ " + tt if tt else "")
    if bt:
        inf["对决"] = bt
    parts = [(r[0], r[1]) for r in c.execute(
        "select speaker,count(*) from lines where script=? and speaker<>'旁白' "
        "group by speaker order by 2 desc limit 12", (script,))]
    secs = [{"h": "场景信息", "html": f"本章共 {lc} 句、{cjk} 字，位于{place or '未注明地点'}。"}]
    if parts:
        secs.append({"h": "出场人物", "people": [{"name": p, "n": n} for p, n in parts]})
    add_page(slug, "场景", title or script, "", inf, secs,
             ["场景", ch] + ([place] if place else []), lc, [ch], sort_key=script)
    if place and f"地点/{place}" in {f"地点/{p}" for p in places}:
        add_link(slug, f"地点/{place}", "发生地", "")
    for p, n in parts:
        if ("人物", p) in name2slug:
            add_link(slug, f"人物/{p}", "出场", str(n))
            add_link(f"人物/{p}", slug, "出场场景", title or script)

# ---------- 词条页（物品/武学/天赋/成就/战斗效果 …）----------
NS_TYPE = {"ItemBook_zh-cn": "物品", "ItemSpecial_zh-cn": "物品", "ItemMisc_zh-cn": "物品",
           "Equipment_zh-cn": "装备", "BattleSkill_zh-cn": "武学", "Talent_zh-cn": "天赋",
           "Library_zh-cn": "成就", "CombatEffects_zh-cn": "战斗效果",
           "Facility_zh-cn": "设施", "CombatCharacter_zh-cn": "战斗角色"}
for ns, eid, kind, title, body in c.execute("select ns,eid,kind,title,body from entries"):
    typ = NS_TYPE.get(ns)
    if not typ or not title:
        continue
    slug = f"{typ}/{title}"
    if any(p[0] == slug for p in pages):
        continue
    inf = {"分类": typ, "编号": eid}
    add_page(slug, typ, title, body or "", inf,
             [{"h": "说明", "html": body or "（暂无说明）"}], [typ], 0, [])

# ---------- 写入 ----------
c.executemany("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?)", pages)
c.executemany("insert into links values(?,?,?,?)",
              [l for l in links if l[0] in {p[0] for p in pages} and l[1] in {p[0] for p in pages}])
c.executemany("insert or replace into redirects values(?,?)", redirects)
c.commit()

print("页面", c.execute("select count(*) from pages").fetchone()[0])
for r in c.execute("select type,count(*) from pages group by type order by 2 desc"):
    print(f"   {r[0]:<6} {r[1]}")
print("链接", c.execute("select count(*) from links").fetchone()[0],
      "重定向", c.execute("select count(*) from redirects").fetchone()[0])
