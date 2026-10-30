# -*- coding: utf-8 -*-
"""事件关闭条件：某事件要求「旗标X = 0」，而另一场剧情把 X 置为 1 —— 那场之后它就不再发生。

只取叙事旗标（E/M/C/S/K 开头或长度≥5 的具名旗标），跳过 A*/TC*/Talk_Option 这类记账旗标。
输出 data/close_cond.json：{事件名: {flag, script, title, time, text}}
"""
import io, sys, os, re, json, sqlite3, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(WIKI, "data", "wiki.db")).cursor()

CONDS = json.load(open(os.path.join(WIKI, "data", "scene_conds.json"), encoding="utf-8"))
TITLE = {s: t for s, t in c.execute("select script,title from scenes")}
ORD = {s: o for s, o in c.execute("select script,ord from scene_order")}
STIME = {s: "%d年%d月%s" % (y, m, x) for s, y, m, x in c.execute("select script,year,month,xun from scene_time")}
EVENTS = collections.defaultdict(list)
for nm, sc in c.execute("select name,script from notes where type='事件'"):
    EVENTS[sc].append(nm)

SETTERS = collections.defaultdict(list)
for sc, flag, val in c.execute("select script,flag,value from flags"):
    if val in ("1", "2", "3", "4", "5", "6"):
        SETTERS[flag].append(sc)

SKIP = re.compile(r"^(A\d+|B\d+|TC\d+|Talk_Option|TalkOption|BattleResult|Dice|Random|R\d+)", re.I)
PAT = re.compile(r"旗标([A-Za-z][A-Za-z0-9_]{2,})\s*[=＝]\s*0")

out = {}
pairs = 0


def handle(sc, texts):
    global pairs
    need = set()
    for tx in texts:
        for m in PAT.finditer(tx or ""):
            f = m.group(1)
            if SKIP.match(f):
                continue
            need.add(f)
    if not need:
        return
    best = None
    for f in need:
        allset = SETTERS.get(f, [])
        if len(allset) > 4:          # 被反复设置的多为计数/开关旗标
            continue
        cur = ORD.get(sc, -1)
        cand = [s for s in allset if s != sc and ORD.get(s, -1) > cur]
        if not cand:
            continue
        cand.sort(key=lambda s: ORD.get(s, 99999))
        t = cand[0]
        if best is None or ORD.get(t, 99999) < ORD.get(best[1], 99999):
            best = (f, t)
    if not best:
        return
    f, t = best
    text = "「%s」之后不再发生（该场把旗标%s置为1）" % (TITLE.get(t) or t, f)
    for nm in EVENTS.get(sc, [])[:3]:
        out.setdefault(nm, {"flag": f, "script": t, "title": TITLE.get(t) or t,
                            "time": STIME.get(t, ""), "text": text})
        pairs += 1


for sc, items in CONDS.items():
    handle(sc, [(it.get("text") or "") for it in items])

# 地图事件的旗标条件同样适用
_pe = json.load(open(os.path.join(WIKI, "data", "position_events.json"), encoding="utf-8"))
_pm = json.load(open(os.path.join(WIKI, "data", "position_script_map.json"), encoding="utf-8"))
for d in _pe:
    sc = _pm.get(d.get("name") or "")
    if not sc:
        continue
    txts = list(d.get("cond") or [])
    for r in d.get("rates") or []:
        txts += list(r.get("cond") or [])
    handle(sc, txts)

json.dump(out, open(os.path.join(WIKI, "data", "close_cond.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("有关闭条件的事件:", len(out), "（写入", pairs, "对）")
for nm in list(out)[:10]:
    v = out[nm]
    print("   %-22s %s" % (nm, v["text"][:70]))
