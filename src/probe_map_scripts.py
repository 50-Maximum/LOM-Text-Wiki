# -*- coding: utf-8 -*-
"""把 PositionEventData 名称 + 配置值 映射到剧本名，测命中率。"""
import io, sys, re, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ev = json.load(open(r"D:\LegendOfMortal Wiki\data\position_events.json", encoding="utf-8"))
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
scripts = {s for (s,) in c.execute("select script from scenes")}
print("剧本数:", len(scripts))


def candidates(d):
    nm, val = d["name"], d["value"]
    out = []
    base = re.sub(r"(_[A-Z]{1,3})?_\d{1,3}$", "", nm)   # 去掉尾部 _E_01 / _01
    for b in {base, nm}:
        low = b.lower()
        if val:
            out.append("%s_%s" % (low, val))
            out.append("%s_%s" % (low, val.zfill(3)))
    return out


hit, miss = [], []
for d in ev:
    m = [x for x in candidates(d) if x in scripts]
    if m:
        hit.append((d, m[0]))
    else:
        miss.append(d)
print("名称+配置值命中剧本: %d / %d" % (len(hit), len(ev)))
for d, s in hit[:10]:
    print("   %-22s %s -> %s | %s" % (d["name"], d["value"], s, "；".join(d["cond"][:2])))
print("\n未命中样例:")
for d in miss[:12]:
    print("   %-22s key=%s value=%s" % (d["name"], d["key"], d["value"]))
