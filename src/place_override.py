# -*- coding: utf-8 -*-
"""1) 生成 39 场「地点填成势力名」的核对表；2) 落地人工核定覆盖表 place_override.json；
3) 给 build_wiki2.place_of 加上覆盖表优先。"""
import io, os, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row

FACTION_ONLY = {"南宫世家", "飞石帮"}   # 唐门/锦香宫 本身也是地点，不算错
rows = []
for r in con.execute("select script,title,chapter,place,cjk from scenes where place<>'' order by script"):
    if r["place"] not in FACTION_ONLY:
        continue
    rows.append(dict(r))
print("待核 %d 场" % len(rows))

KEY = ["唐门", "江陵", "卧云岗", "眉山", "襄阳", "崆峒", "成都", "锦香宫", "青城", "峨嵋"]
buf = ["地点填成势力名：%d 场待核（南宫世家／飞石帮）\n" % len(rows)]
pick = {}
for d in rows:
    lines = list(con.execute("select seq, speaker, text from lines where script=? order by seq",
                             (d["script"],)))
    cnt = collections.Counter()
    for _, _, t in lines:
        for k in KEY:
            if k in (t or ""):
                cnt[k] += (t or "").count(k)
    top = [k for k, _ in cnt.most_common(3)]
    buf.append("%s｜%s｜%s｜%d 字｜现标：%s" % (d["script"], d["title"] or "", d["chapter"],
                                           d["cjk"], d["place"]))
    buf.append("   出现：%s" % ("、".join("%s×%d" % (k, v) for k, v in cnt.most_common(4)) or "（无）"))
    shown = 0
    for seq, sp, t in lines:
        t = t or ""
        if any(k in t for k in KEY) and shown < 2:
            buf.append("   #%d %s %s" % (seq, (sp or "")[:8], t[:100]))
            shown += 1
    buf.append("")
    pick[d["script"]] = top[0] if top else ""

open(os.path.join(BASE, "data", "place_faction_audit.md"), "w", encoding="utf-8").write("\n".join(buf))
print("核对表 data/place_faction_audit.md")

# ---- 人工核定（第 1 批，已逐场看原文）----
OV = {
    "ch4_4_1": {"place": "唐门", "why": "唐升、唐惟元、赵活在门中论飞石帮催战信，原文「唐门不过是一户姓唐的人家，结庐在蜀中」"},
    "ch4_1_3": {"place": "唐门", "why": "飞石帮登门叫阵，唐惟元、郁竹、唐铮在门前应对，旁白写街坊围观"},
    "ch7_2_4": {"place": "唐门", "why": "魏菊与唐升论武林盟檄书，原文「唐门比之崆峒，待着舒心太多了」"},
    "ch2_4_4_1": {"place": "", "why": "青城、峨嵋弟子在客店备马打酒，众人尚未到江陵，文中未写店在何处"},
}
p = os.path.join(BASE, "data", "place_override.json")
old = {}
if os.path.exists(p):
    old = json.load(open(p, encoding="utf-8"))
old.update(OV)
json.dump(old, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("覆盖表 %d 条 -> data/place_override.json" % len(old))

# ---- 给 place_of 加覆盖 ----
S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()
if "PLACE_OVERRIDE" not in s:
    load_anchor = 'PLACE_INFER = json.load(open(_pip, encoding="utf-8"))'
    assert load_anchor in s
    s = s.replace(load_anchor, load_anchor + '''

# 人工核定：逐场看过原文的地点修正（data/place_override.json）
PLACE_OVERRIDE = {}
try:
    _pov = os.path.join(BASE, "data", "place_override.json")
    if os.path.exists(_pov):
        PLACE_OVERRIDE = json.load(open(_pov, encoding="utf-8"))
except Exception:
    PLACE_OVERRIDE = {}''', 1)
    head = 'def place_of(script):\n    """返回 (地点, 依据)。'
    assert head in s
    s = s.replace(head, '''def place_of(script):
    _ov = PLACE_OVERRIDE.get(script)
    if _ov is not None:
        _pv = pcanon(_ov.get("place") or "")
        return _pv, ("人工核定" if _pv else "证据不足")
    """返回 (地点, 依据)。''', 1)
    open(S, "w", encoding="utf-8").write(s)
    print("build_wiki2：place_of 已支持人工核定覆盖")
else:
    print("build_wiki2：已有覆盖逻辑，跳过")
