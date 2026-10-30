# -*- coding: utf-8 -*-
"""第一步：门派归属推断 + 门派表。"""
import sqlite3, re, collections

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
c.execute("PRAGMA journal_mode=WAL")

FACTIONS = [
    ("唐门", "门派", "蜀中唐门，暗器名家。"),
    ("青城派", "门派", "青城山道门，正一盟威。"),
    ("崆峒派", "门派", "崆峒山武学，飞天殿一脉。"),
    ("全真教", "门派", "道门正宗。"),
    ("峨嵋派", "门派", "峨嵋山门派。"),
    ("衡山派", "门派", "衡山剑派。"),
    ("点苍派", "门派", "点苍山剑派。"),
    ("南宫世家", "世家", "武林世家。"),
    ("上官世家", "世家", "武林世家。"),
    ("锦香宫", "势力", "江湖势力。"),
    ("丐帮", "帮会", "天下第一大帮。"),
    ("飞石帮", "帮会", "地方帮会。"),
    ("泥教", "教派", "江湖教派。"),
]
NAME2F = {n: n for n, _, _ in FACTIONS}
# 简称与别名
ALIAS = {
    "唐门": ["唐门", "唐家堡"], "青城派": ["青城派", "青城"], "崆峒派": ["崆峒派", "崆峒"],
    "全真教": ["全真教", "全真"], "峨嵋派": ["峨嵋派", "峨嵋", "峨眉"],
    "衡山派": ["衡山派", "衡山"], "点苍派": ["点苍派", "点苍"],
    "南宫世家": ["南宫世家", "南宫家"], "上官世家": ["上官世家", "上官家"],
    "锦香宫": ["锦香宫"], "丐帮": ["丐帮"], "飞石帮": ["飞石帮"], "泥教": ["泥教"],
}
PLACE2F = {"唐门": "唐门", "崆峒": "崆峒派", "青城": "青城派"}

c.execute("DROP TABLE IF EXISTS factions")
c.execute("CREATE TABLE factions(name TEXT PRIMARY KEY, kind TEXT, desc TEXT)")
c.executemany("INSERT INTO factions VALUES(?,?,?)", FACTIONS)

c.execute("DROP TABLE IF EXISTS char_faction")
c.execute("CREATE TABLE char_faction(char_id TEXT PRIMARY KEY, faction TEXT, score INT, method TEXT)")

names = {r["id"]: r["name"] for r in c.execute("SELECT id,name FROM names")}
intros = collections.defaultdict(str)
for r in c.execute("SELECT eid,body FROM entries WHERE ns='CharacterIntro_zh-cn'"):
    intros[r["eid"]] += r["body"] or ""

place_by_char = collections.defaultdict(collections.Counter)
for r in c.execute("""SELECT l.speaker_id cid, s.root root, COUNT(*) n FROM lines l
                      JOIN scenes s ON s.script=l.script
                      WHERE l.speaker_id IS NOT NULL AND s.root<>'' GROUP BY cid, root"""):
    place_by_char[r["cid"]][r["root"]] = r["n"]

self_text = collections.defaultdict(str)
for r in c.execute("SELECT speaker_id cid, text FROM lines WHERE speaker_id IS NOT NULL AND text<>''"):
    if len(self_text[r["cid"]]) < 20000:
        self_text[r["cid"]] += r["text"] + "\n"

rows = []
for cid, nm in names.items():
    scores = collections.Counter()
    methods = {}
    # 名字
    for f, aliases in ALIAS.items():
        if any(a in nm for a in aliases):
            scores[f] += 5
            methods.setdefault(f, "名字")
    # 人物介绍
    intro = intros.get(cid, "")
    for f, aliases in ALIAS.items():
        if any(a in intro for a in aliases):
            scores[f] += 3
            methods.setdefault(f, "介绍")
    # 活动地点
    pc = place_by_char.get(cid)
    if pc:
        tot = sum(pc.values())
        for root, n in pc.items():
            f = PLACE2F.get(root)
            if f and n / tot >= 0.5:
                scores[f] += 3
                methods.setdefault(f, "活动地点")
    # 自称
    st = self_text.get(cid, "")
    for f, aliases in ALIAS.items():
        n = sum(st.count(a) for a in aliases)
        if n:
            scores[f] += min(n, 3)
            methods.setdefault(f, "自称")
    if scores:
        f, sc = scores.most_common(1)[0]
        if sc >= 2:
            rows.append((cid, f, sc, methods.get(f, "")))
c.executemany("INSERT OR REPLACE INTO char_faction VALUES(?,?,?,?)", rows)
c.commit()

print("factions:", len(FACTIONS), "assigned:", len(rows), "chars:", len(names))
dist = collections.Counter(r[1] for r in rows)
print("分布:", dist.most_common(10))
print("未归属:", len(names) - len(rows))
