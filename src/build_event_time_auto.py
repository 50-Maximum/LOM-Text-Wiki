# -*- coding: utf-8 -*-
"""事件时间逻辑推导（自动部分）：
  1. 直接时间：scene_time（攻略给的年月旬）
  2. 沿进入边传播：上一场有时间且为接续/选择，则这一场不早于它
  3. 地图事件时间窗：能对上的事件加上起止
输出 data/event_time_auto.json：{事件名: {earliest, latest, basis}}
"""
import io, sys, os, json, sqlite3, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(WIKI, "data", "wiki.db")).cursor()

XUN = {"上旬": 0, "中旬": 1, "下旬": 2}


def key(y, m, x):
    return int(y) * 100 + int(m) * 10 + XUN.get(x, 0)


def label(y, m, x):
    return "%d年%d月%s" % (int(y), int(m), x)


STIME = {}
for s, y, m, x in c.execute("select script,year,month,xun from scene_time"):
    if y and m and x:
        STIME[s] = (int(y), int(m), x, key(y, m, x), label(y, m, x))

EDGES = json.load(open(os.path.join(WIKI, "data", "entry_edges.json"), encoding="utf-8"))
PRED = collections.defaultdict(list)          # 目标 -> [(源, 类型)]
for tgt, rows in EDGES.items():
    for r in rows:
        PRED[tgt].append((r.get("src") or "", r.get("kind") or ""))

# 1) 传播：广度优先，最多 3 跳
INFER = {}
for s in list(STIME):
    INFER[s] = (STIME[s][3], STIME[s][4], "攻略给出")
changed = True
hops = 0
while changed and hops < 3:
    changed = False
    hops += 1
    for tgt, preds in PRED.items():
        if tgt in INFER:
            continue
        for src, kind in preds:
            if src in INFER and kind in ("接续", "选择", "判定", "条件"):
                k, lb, why = INFER[src]
                INFER[tgt] = (k, lb, "上一场「%s」为%s（%s）" % (src, lb, kind))
                changed = True
                break

# 2) 地图事件时间窗
POS = json.load(open(os.path.join(WIKI, "data", "position_events.json"), encoding="utf-8"))
PMAP = json.load(open(os.path.join(WIKI, "data", "position_script_map.json"), encoding="utf-8"))
WINDOW = {}
for d in POS:
    sc = PMAP.get(d["name"])
    if sc and (d.get("start") or d.get("end")):
        WINDOW[sc] = (d.get("start"), d.get("end"))

# 3) 事件名 -> 脚本
EV = collections.defaultdict(set)
for nm, sc in c.execute("select name,script from notes where type='事件'"):
    EV[nm].add(sc)

out = {}
TITLE = {s: t for s, t in c.execute("select script,title from scenes")}
for nm, scs in EV.items():
    best = None
    for sc in scs:
        if sc in STIME:
            best = (STIME[sc][3], STIME[sc][4], "直接", None, "")
            break
    if not best:
        for sc in scs:
            if sc in INFER:
                k, lb, why = INFER[sc]
                best = (k, lb, "传播", why, sc)
                break
    win = None
    for sc in scs:
        if sc in WINDOW:
            win = WINDOW[sc]
            break
    if not best and not win:
        continue
    if best and best[2] == "直接" and not win:
        continue          # 信息框已有直接时间，不重复显示
    e = {"earliest": (best[1] if best else (win[0] if win else "")),
         "latest": (win[1] if win and win[1] else ""),
         "basis": ""}
    bits = []
    if best and best[2] == "直接":
        bits.append("攻略标注本场发生在%s" % best[1])
    elif best:
        src = best[3].split("「")[1].split("」")[0] if "「" in best[3] else ""
        st = TITLE.get(src) or src or "上一场"
        if st in ("None", "null"):
            st = "上一场"
        kind = best[3].split("（")[-1].rstrip("）") if "（" in best[3] else "接续"
        bits.append("上一场「%s」为%s，本场紧随其后（%s）" % (st, best[1], kind))
    if win:
        if win[0]:
            bits.append("地图事件时间窗起于%s" % win[0])
        if win[1]:
            bits.append("止于%s" % win[1])
    e["basis"] = "；".join(bits) + "。"
    out["事件/" + nm] = e

json.dump(out, open(os.path.join(WIKI, "data", "event_time_auto.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("事件页 %d，推导出时间 %d" % (len(EV), len(out)))
dirs = collections.Counter("攻略标注" if "攻略标注" in v["basis"] else ("传播" if "上一场" in v["basis"] else "地图窗") for v in out.values())
print("来源:", dict(dirs))
for nm in list(out)[:8]:
    print("\n ", nm)
    print("    最早:", out[nm]["earliest"], " 最晚:", out[nm]["latest"] or "—")
    print("    依据:", out[nm]["basis"][:90])
