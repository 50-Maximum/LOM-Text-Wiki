# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"

pre = json.load(open(B + r"\chars_prefix.json", encoding="utf-8"))
pre.update({"虞小梅": "崆峒", "夏侯兰": "崆峒", "阿鹤侠": "崆峒",
            "魏菊": "崆峒", "丹霞子": "崆峒", "金乌上人": "崆峒"})
json.dump(pre, open(B + r"\chars_prefix.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("前缀覆盖", len(pre))

p = B + r"\chars_fix.json"
d = json.load(open(p, encoding="utf-8"))
M = d.setdefault("merge", {})
n0 = len(M)
M["鹤手"] = "阿鹤侠"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("合并", n0, "→", len(M))
