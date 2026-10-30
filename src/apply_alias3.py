# -*- coding: utf-8 -*-
"""第三轮：绰号合并 + 门派前缀修正。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"

p = B + r"\chars_fix.json"
d = json.load(open(p, encoding="utf-8"))
M = d.setdefault("merge", {})
add = {
    "裂骨魔": "郁竹", "崆峒裂骨魔": "郁竹",
    "夺魄幽兰": "夏侯兰",
    "苍松剑客": "叶云舟",
    "萤姑娘": "上官萤",
    "向掌门": "向无忧",
    "石帮主": "石公远",
    "雷掌门": "雷谦", "雷老大": "雷谦",
    "王帮主": "王二壮",
    "孟县主": "孟仙谣", "枣阳孟县主": "孟仙谣",
    "千面人魔": "画中仙",
    "宝花": "郁宝花",
}
n0 = len(M)
M.update(add)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("merge %d → %d" % (n0, len(M)))

# 门派前缀（原文有明确证据）
pre = {
    "高和子": "青城", "怀素真人": "青城", "不平道长": "青城",
    "停风子": "青城", "清虚子": "青城",
    "郁竹": "铁拳门", "郁城": "铁拳门", "郁父": "铁拳门", "郁母": "铁拳门",
    "赵活的娘": "唐门", "叶父": "叶家", "叶云啾": "叶家",
    "姚知命": "崆峒",
}
json.dump(pre, open(B + r"\chars_prefix.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("前缀覆盖", len(pre), "人")
