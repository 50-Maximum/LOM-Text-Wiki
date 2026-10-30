# -*- coding: utf-8 -*-
"""按全文挖掘结果重建势力表，并改进归属推断（含家族姓氏规则）。"""
import sqlite3, re, json, collections

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
CAND = r"D:\LegendOfMortal Wiki\data\summary\势力候选.json"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row

NOISE = ("掌门", "掌派", "大会", "不会", "一定", "可能", "没人", "各位", "参见",
         "启禀", "多谢", "在下", "该", "也", "就", "才", "但", "并且", "如果",
         "虽然", "然后", "所有", "这些", "那些", "各大", "六大", "武林", "门派",
         "弟子", "众人", "我们", "你们", "他们", "咱们")

KIND_SUFFIX = [("世家", "世家"), ("派", "门派"), ("门", "门派"), ("楼", "势力"),
               ("阁", "势力"), ("教", "教派"), ("帮", "帮会"), ("宫", "势力"),
               ("盟", "组织"), ("会", "组织"), ("山", "地点"), ("谷", "地点"),
               ("庄", "势力"), ("寨", "势力"), ("岛", "势力"), ("城", "地点"),
               ("寺", "门派"), ("观", "门派"), ("宗", "门派")]

CANON = ["唐门", "崆峒派", "青城派", "衡山派", "点苍派", "全真教", "峨嵋派",
         "雪山派", "飞天门", "铁拳门", "夺魄门", "玄功门", "极乐教", "飞石帮",
         "锦香宫", "南宫世家", "上官世家", "千灯楼", "火炎山剑阁", "西武林盟",
         "武林盟", "铁掌门", "逍遥会", "白鲨帮", "风雨山"]

cands = json.load(open(CAND, encoding="utf-8"))
names = set(CANON)
for n, k in cands:
    if k < 8:
        continue
    if any(x in n for x in NOISE):
        continue
    if len(n) < 3 or len(n) > 8:
        continue
    names.add(n)

def kind_of(n):
    for suf, kind in KIND_SUFFIX:
        if n.endswith(suf):
            return kind
    return "势力"

rows = [(n, kind_of(n), "") for n in sorted(names)]
c.execute("DROP TABLE IF EXISTS factions")
c.execute("CREATE TABLE factions(name TEXT PRIMARY KEY, kind TEXT, desc TEXT)")
c.executemany("INSERT INTO factions VALUES(?,?,?)", rows)

def aliases(n):
    a = {n}
    for suf in ("派", "门", "楼", "阁", "教", "帮", "宫", "盟", "会", "山", "谷", "庄", "寨", "岛", "城", "寺", "观", "宗", "世家"):
        if n.endswith(suf) and len(n) > len(suf) + 1:
            a.add(n[:-len(suf)])
    if n == "唐门":
        a.add("唐家堡")
    return a

ALIAS = {n: aliases(n) for n in names}
SURNAME = {"上官": "上官世家", "南宫": "南宫世家", "唐": "唐门"}
PLACE2F = {"唐门": "唐门", "崆峒": "崆峒派", "青城": "青城派"}

names_map = {r["id"]: r["name"] for r in c.execute("SELECT id,name FROM names")}
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

c.execute("DROP TABLE IF EXISTS char_faction")
c.execute("CREATE TABLE char_faction(char_id TEXT PRIMARY KEY, faction TEXT, score INT, method TEXT)")
out = []
for cid, nm in names_map.items():
    scores = collections.Counter()
    methods = {}
    for f, al in ALIAS.items():
        if any(a in nm for a in al):
            scores[f] += 5
            methods.setdefault(f, "名字")
    for pre, f in SURNAME.items():
        if nm.startswith(pre) and f in names:
            scores[f] += 6
            methods.setdefault(f, "姓氏")
    intro = intros.get(cid, "")
    for f, al in ALIAS.items():
        if any(a in intro for a in al):
            scores[f] += 3
            methods.setdefault(f, "介绍")
    pc = place_by_char.get(cid)
    if pc:
        tot = sum(pc.values())
        for root, n in pc.items():
            f = PLACE2F.get(root)
            if f and n / tot >= 0.5:
                scores[f] += 3
                methods.setdefault(f, "活动地点")
    st = self_text.get(cid, "")
    for f, al in ALIAS.items():
        n = sum(st.count(a) for a in al)
        if n:
            scores[f] += min(n, 3)
            methods.setdefault(f, "自称")
    if scores:
        f, sc = scores.most_common(1)[0]
        if sc >= 2:
            out.append((cid, f, sc, methods.get(f, "")))

c.executemany("INSERT OR REPLACE INTO char_faction VALUES(?,?,?,?)", out)
c.commit()
dist = collections.Counter(r[1] for r in out)
print("factions:", len(rows), "assigned:", len(out))
for f, n in dist.most_common(35):
    print(f"{n:4d}  {f}")
print("上官世家:", [r for r in out if r[1] == "上官世家"][:6])
