# -*- coding: utf-8 -*-
"""条件噪声过滤（用 items 推阶段，避免未定义 facet）+ 段考约战归位。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"

arcs = json.load(open(os.path.join(B, "arcs.json"), encoding="utf-8"))
arcs.setdefault("scene", {})["S8400_01_01"] = "外姓弟子"
json.dump(arcs, open(os.path.join(B, "arcs.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("S8400_01_01 → 外姓弟子")

s = open(P, encoding="utf-8").read().replace("\r\n", "\n")
old = """            _crow2 = [r for r in _crow2
                      if not re.match(r"^\\s*备注[:：]", (r.get("note") or ""))
                      and "差分" not in (r.get("note") or "")
                      and "第三年" not in (r.get("note") or "")]"""
new = """            _a0 = arc_of(items[0]["script"]) if items else ""
            _fidx = ARC_ORDER.index(_a0) if _a0 in ARC_ORDER else 99
            _late = ARC_ORDER.index("武林盟进攻唐门") if "武林盟进攻唐门" in ARC_ORDER else 6
            _crow2 = [r for r in _crow2
                      if not re.match(r"^\\s*备注[:：]", (r.get("note") or ""))
                      and "差分" not in (r.get("note") or "")
                      and "第三年" not in (r.get("note") or "")
                      and not (_fidx < _late and ("武林盟" in (r.get("note") or "")
                                                  or "西武林" in (r.get("note") or "")))]"""
if old in s:
    s = s.replace(old, new, 1)
    open(P, "w", encoding="utf-8", newline="\n").write(s)
    print("早期事件不再挂武林盟条件")
else:
    print("未匹配到噪声过滤块")
