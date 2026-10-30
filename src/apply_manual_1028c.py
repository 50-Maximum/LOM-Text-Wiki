# -*- coding: utf-8 -*-
"""收尾第三批：大理段氏→大理、饿鬼道→泥教 统一到筛选层；补刘颚归属。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")
old = '    "岭南剑派": "岭南派",\n'
new = ('    "岭南剑派": "岭南派",\n'
       '    "大理段氏": "大理",\n'
       '    "饿鬼道": "泥教",\n'
       '    "吕氏商会": "市井",\n')
if "大理段氏" not in s.split("FAC_NORM")[1][:400]:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("FAC_NORM 已补：大理段氏→大理、饿鬼道→泥教、吕氏商会→市井")
else:
    print("FAC_NORM 已有对应项")

q = r"D:\LegendOfMortal Wiki\data\chars_prefix.json"
cp = json.load(open(q, encoding="utf-8"))
cp.update({"刘颚": "泥教", "赵逵": "泥教"})
json.dump(cp, open(q, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("刘颚/赵逵 → 泥教")
