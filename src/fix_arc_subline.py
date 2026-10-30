# -*- coding: utf-8 -*-
"""支线/其他 章节不按日期推阶段，避免 2年10月 被算成江陵围城。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

old = """def arc_of(script):
    if script in ARC_SC:
        return ARC_SC[script]
    st = STIME.get(script)"""
new = """def arc_of(script):
    if script in ARC_SC:
        return ARC_SC[script]
    _ch0 = (scenes.get(script) or {}).get("chapter") or ""
    if _ch0 in ("支线", "其他", "角色线"):
        ch_ = ARC_CH.get(_ch0)
        if ch_:
            return ch_
        return "不限时间"
    st = STIME.get(script)"""
if old in s:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("arc_of：支线/其他 不再按日期推阶段")
else:
    print("未匹配 arc_of")
