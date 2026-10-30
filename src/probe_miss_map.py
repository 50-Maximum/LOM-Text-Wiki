# -*- coding: utf-8 -*-
"""给未映射的地图事件找最接近的剧本名，打印候选，便于定规则。"""
import io, sys, re, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ev = json.load(open(r"D:\LegendOfMortal Wiki\data\position_events.json", encoding="utf-8"))
mp = json.load(open(r"D:\LegendOfMortal Wiki\data\position_script_map.json", encoding="utf-8"))
cb = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
scripts = [r[0] for r in cb.execute("select script from scenes")]
S = set(scripts)
miss = [d for d in ev if d["name"] not in mp]
print("未映射:", len(miss))
for d in miss[:14]:
    nm = d["name"].lower()
    base = re.sub(r"(_[a-z]{1,3})?_\d{1,3}$", "", nm)
    val = d["value"]
    prox = [s for s in scripts if s.startswith(base)][:6]
    anyval = [s for s in scripts if s.startswith(base) and s.endswith(val)][:4] if val else []
    print("\n %-24s val=%s base=%s" % (d["name"], val, base))
    print("    前缀相近:", prox)
    print("    尾号同值:", anyval)
    print("    条件:", "；".join(d["cond"][:2]) or "（无）")
