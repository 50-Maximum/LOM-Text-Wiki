# -*- coding: utf-8 -*-
"""25 个未映射地图事件：打印完整字段 + 按结果码族找候选剧本。"""
import io, sys, json, sqlite3, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
ev = json.load(open(B + r"\position_events.json", encoding="utf-8"))
mp = json.load(open(B + r"\position_script_map.json", encoding="utf-8"))
c = sqlite3.connect(B + r"\wiki.db").cursor()
SC = [r[0] for r in c.execute("select script from scenes")]
titles = dict(c.execute("select script,title from scenes"))

miss = [d for d in ev if d["name"] not in mp]
seen = set()
for d in miss:
    nm, val = d["name"], str(d.get("value") or "")
    if (nm, val) in seen:
        continue
    seen.add((nm, val))
    fam = []
    if re.match(r"(?i)^travel", nm):
        fam = [s for s in SC if re.search(r"(?i)travel_result_\d+_" + re.escape(val) + "$", s)]
    elif re.match(r"(?i)^door", nm):
        fam = [s for s in SC if re.match(r"(?i)door", s) and s.endswith("_" + val)]
    elif re.match(r"(?i)^section", nm):
        m = re.match(r"(?i)section_(\d+)_(\d+)", nm)
        fam = [s for s in SC if s.startswith("section_%s_free_%s" % (m.group(1), m.group(2)))]
    print("\n%-24s val=%-8s key=%-8s 概率%-4s 候选 %d"
          % (nm, val, d.get("key"), d.get("rate"), len(fam)))
    for s in fam[:6]:
        print("     %-38s %s" % (s, (titles.get(s) or "")[:26]))
