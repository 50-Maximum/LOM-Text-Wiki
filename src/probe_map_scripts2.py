# -*- coding: utf-8 -*-
"""扩充候选写法，提高 PositionEventData → 剧本 的命中率。"""
import io, sys, re, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ev = json.load(open(r"D:\LegendOfMortal Wiki\data\position_events.json", encoding="utf-8"))
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
scripts = {s for (s,) in c.execute("select script from scenes")}


def cands(d):
    nm, val = d["name"], d["value"]
    base = re.sub(r"(_[A-Z]{1,3})?_\d{1,3}$", "", nm)
    outs = []
    for b in {base, nm}:
        low = b.lower()
        outs += [low, low.replace("ch_", "ch")]
    res = []
    for b in outs:
        if val:
            res += [b + "_" + val, b + "_" + val.zfill(3), b + val, b + val.zfill(3)]
        res.append(b)
    return list(dict.fromkeys(res))


hit = {}
miss = []
for d in ev:
    m = [x for x in cands(d) if x in scripts]
    if m:
        hit[d["name"]] = m[0]
    else:
        miss.append(d)
print("命中 %d / %d" % (len(hit), len(ev)))
for nm in list(hit)[:8]:
    print("   ", nm, "->", hit[nm])
print("\n仍未命中 %d 个，样例：" % len(miss))
for d in miss[:10]:
    print("   %-24s key=%s val=%s" % (d["name"], d["key"], d["value"]))
json.dump(hit, open(r"D:\LegendOfMortal Wiki\data\position_script_map.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("写出 data/position_script_map.json")
