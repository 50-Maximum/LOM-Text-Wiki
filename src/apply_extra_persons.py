# -*- coding: utf-8 -*-
"""补齐「有名字但没建页」的角色：只写原文能证明的内容。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"

extra = {
    "孟瞋": {"faction": "崆峒派", "sub": "铁拳门"},
    "温无畏": {"faction": "峨嵋派"},
    "阮蛋": {"faction": "岭南派"},
    "阿叔": {"faction": "丐帮"},
    "唐鹿": {"faction": "唐门"},
    "米欧宽": {"faction": "岭南派"},
}
json.dump(extra, open(B + r"\extra_persons.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# 别名与门派补齐
p = B + r"\chars_fix.json"
d = json.load(open(p, encoding="utf-8"))
M = d.setdefault("merge", {})
for a, b in {"明玉": "明玉夫人", "觉慧": "觉慧方丈", "觉醒": "觉醒禅师"}.items():
    M[a] = b
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pp = B + r"\chars_prefix.json"
pre = json.load(open(pp, encoding="utf-8"))
pre.update({"明玉夫人": "锦香宫", "觉慧方丈": "嵩山派", "觉醒禅师": "嵩山派"})
json.dump(pre, open(pp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("extra 人物 %d，合并 %d，前缀 %d" % (len(extra), len(M), len(pre)))
