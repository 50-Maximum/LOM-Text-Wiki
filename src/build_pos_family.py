# -*- coding: utf-8 -*-
"""未映射的地图事件：按「结果码」找同型剧本族，输出 data/position_script_family.json

原则：这些事件在游戏里是按路线复用同一套结果剧本（travel_result_<路线>_<结果码>），
不能唯一对应某一场戏，只能给出同码的剧本清单。
"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
ev = json.load(open(B + r"\position_events.json", encoding="utf-8"))
mp = json.load(open(B + r"\position_script_map.json", encoding="utf-8"))
c = sqlite3.connect(B + r"\wiki.db").cursor()
SC = [r[0] for r in c.execute("select script from scenes")]

def family(nm, val):
    val = str(val or "")
    if re.match(r"(?i)^travel", nm):
        return [s for s in SC
                if re.search(r"(?i)^travel_result_\d+_" + re.escape(val) + "$", s)]
    if re.match(r"(?i)^section", nm):
        m = re.match(r"(?i)^section_(\d+)_(\d+)_(\d+)", nm)
        if not m:
            return []
        base = "section_%s_free_%s_%s" % (m.group(1), m.group(2), m.group(3))
        return [s for s in SC if s.startswith(base + "_") and s.endswith("_" + val)]
    if re.match(r"(?i)^door", nm):
        return [s for s in SC
                if re.match(r"(?i)^door", s) and s.endswith("_" + val)]
    return []

out, stats = {}, {"travel": 0, "section": 0, "door": 0, "none": 0}
for d in ev:
    nm = d["name"]
    if nm in mp:
        continue
    fam = family(nm, d.get("value"))
    if not fam:
        stats["none"] += 1
        continue
    out.setdefault(nm, [])
    for s in fam:
        if s not in out[nm]:
            out[nm].append(s)
    stats["travel" if nm.lower().startswith("travel")
          else "section" if nm.lower().startswith("section") else "door"] += 1

json.dump(out, open(B + r"\position_script_family.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("同型族 %d 个事件名，覆盖条目 %d" % (len(out), sum(len(v) for v in out.values())))
print("分类:", stats)
for nm, fam in sorted(out.items()):
    print("   %-24s %d 条：%s" % (nm, len(fam), "、".join(fam[:4])))
