# -*- coding: utf-8 -*-
"""看 CB 里有没有 ch6_6_2_break_start_01，以及 TM 的 talk 块结构。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
CB = json.load(open(B + r"\choice_branch.json", encoding="utf-8"))
TM = json.load(open(B + r"\talk_menus.json", encoding="utf-8"))
print("CB 有该剧本:", "ch6_6_2_break_start_01" in CB)
print("TM 块:", [(b["var"], len(b["options"])) for b in TM.get("ch6_6_2_break_start_01", [])])
print("\nTM 第一个 talk 块前 3 项:")
for b in TM.get("ch6_6_2_break_start_01", []):
    if b["var"] == "talk":
        for o in b["options"][:3]:
            print("  ", o)
        break
# CB 与 TM 变量重叠统计
both = 0
for sc, blocks in TM.items():
    cbvars = {x.get("var") for x in (CB.get(sc) or [])}
    if cbvars & {b["var"] for b in blocks}:
        both += 1
print("\nCB/TM 变量重叠的剧本数:", both, "/", len(TM))
