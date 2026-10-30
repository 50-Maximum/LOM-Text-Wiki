# -*- coding: utf-8 -*-
"""收尾：删掉多余的 势力/孤云山（并入 孤云山派），并把瑞笙前缀改成孤云山派。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"

p = os.path.join(B, "factions_fix.json")
d = json.load(open(p, encoding="utf-8"))
dele = d.setdefault("delete", [])
if "孤云山" not in dele:
    dele.append("孤云山")
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("factions_fix.delete += 孤云山")

q = os.path.join(B, "chars_prefix.json")
cp = json.load(open(q, encoding="utf-8"))
if cp.get("瑞笙") != "孤云山派":
    print("瑞笙 前缀", cp.get("瑞笙"), "→ 孤云山派")
    cp["瑞笙"] = "孤云山派"
    json.dump(cp, open(q, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
