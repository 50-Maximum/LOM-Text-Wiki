# -*- coding: utf-8 -*-
"""把场景按「无条件接续」合成剧情段；并判定主线 / 支线。

主线：从章节起点只靠无条件接续就能走到 —— 必然发生。
支线：必须满足条件（判定/选项）才进得去。
"""
import io, os, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")
NXT = json.load(open(os.path.join(D, "scene_next.json"), encoding="utf-8"))

SCENES = {}
c = sqlite3.connect(os.path.join(D, "wiki.db")).cursor()
for s, t in c.execute("select script,title from scenes"):
    SCENES[s] = t


def title(s):
    return SCENES.get(s) or s


# ---------- 1. 主线 / 支线 ----------
uncond_in, cond_in = {}, {}
for s, d in NXT.items():
    t = (d or {}).get("next")
    if t:
        uncond_in.setdefault(t, []).append(s)
    for e in (d or {}).get("edges") or []:
        t2 = e.get("target")
        if t2:
            cond_in.setdefault(t2, []).append(s)

main = set()
for s in SCENES:
    if s not in uncond_in and s not in cond_in:
        main.add(s)          # 无入口 = 章节起点

def forced_next(s):
    """无条件接续；若所有条件分支都指向同一场，也算必然。"""
    d = NXT.get(s) or {}
    nx = d.get("next")
    if nx:
        return nx
    ts = {e.get("target") for e in (d.get("edges") or []) if e.get("target")}
    if len(ts) == 1:
        return ts.pop()
    return None


changed = True
while changed:
    changed = False
    for s in list(main):
        t = forced_next(s)
        if t in SCENES and t not in main:
            main.add(t)
            changed = True

route_of = {s: ("主线" if s in main else "支线") for s in SCENES}

# ---------- 2. 合段 ----------
inc = set()
for s, d in NXT.items():
    t = (d or {}).get("next")
    if t:
        inc.add(t)

starts = sorted(s for s in NXT if s in SCENES and s not in inc)
lonely = [s for s in SCENES if s not in NXT]
seg_of, segs = {}, []


def walk(start):
    path, cur, seen = [], start, set()
    while cur and cur not in seen:
        seen.add(cur)
        path.append(cur)
        nxt = forced_next(cur)
        if nxt and (nxt not in SCENES or nxt in seg_of):
            break
        cur = nxt
    return path


n = 0
for s in starts:
    if s in seg_of:
        continue
    path = [p for p in walk(s) if p in SCENES]
    if not path:
        continue
    n += 1
    sid = "S%03d" % n
    for p in path:
        seg_of[p] = sid
    segs.append({"id": sid, "scenes": path})

for s in lonely:
    if s in seg_of:
        continue
    n += 1
    sid = "S%03d" % n
    seg_of[s] = sid
    segs.append({"id": sid, "scenes": [s]})

# ---------- 3. 段的出口与主线判定 ----------
for sg in segs:
    last = sg["scenes"][-1]
    d = NXT.get(last) or {}
    nxt = d.get("next")
    branches, seen_b = [], set()
    for e in (d.get("edges") or []):
        t = e.get("target")
        if not t or t == nxt:
            continue
        bseg = seg_of.get(t, "")
        if not bseg or bseg == sg["id"] or bseg in seen_b:
            continue
        seen_b.add(bseg)
        branches.append({"seg": bseg, "to": t, "cond": (e.get("cond") or "").strip()})
    sg["last"] = last
    sg["next_seg"] = seg_of.get(nxt, "") if nxt else ""
    sg["next_scene"] = nxt or ""
    sg["branches"] = branches[:8]
    sg["title"] = title(sg["scenes"][0])
    # 全段都靠无条件接续才成立的，才是主线
    sg["route"] = "主线" if all(route_of.get(x) == "主线" for x in sg["scenes"]) else "支线"
    sg["cond"] = next((b["cond"] for b in branches if b["cond"]), "")

json.dump({"segments": segs, "seg_of": seg_of,
           "route_of": route_of,
           "titles": {k: title(k) for k in SCENES}},
          open(os.path.join(D, "story_segments.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("剧情段 %d 个，覆盖场景 %d / %d" % (len(segs), len(seg_of), len(SCENES)))
print("主线场景 %d，支线场景 %d" % (len(main), len(SCENES) - len(main)))
print("主线段 %d，支线段 %d" % (sum(1 for s in segs if s["route"] == "主线"),
                                sum(1 for s in segs if s["route"] == "支线")))
multi = [s for s in segs if len(s["scenes"]) > 1]
print("多场段 %d 个，最长 %d 场" % (len(multi), max((len(s["scenes"]) for s in segs), default=0)))
for s in segs[:4]:
    print("  %s %s（%d 场，%s）→ %s" % (s["id"], s["title"][:18], len(s["scenes"]),
                                        s["route"], s["next_seg"] or "无接续"))
