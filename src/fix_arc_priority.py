# -*- coding: utf-8 -*-
"""阶段判定优先级：人工场景表 > 章节 > 标题关键词 > 攻略日期。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

start = s.index("def arc_of(script):")
end = s.index("for _s, _v in scenes.items():")
new_fn = '''def arc_of(script):
    # 1) 人工指定优先
    if script in ARC_SC:
        return ARC_SC[script]
    _ch0 = (scenes.get(script) or {}).get("chapter") or ""
    # 2) 支线/其他/角色线：不按日期推，直接上限
    if _ch0 in ("支线", "其他", "角色线"):
        return ARC_CH.get(_ch0) or "不限时间"
    # 3) 章节是硬归属
    if _ch0 in ARC_CH and ARC_CH[_ch0]:
        return ARC_CH[_ch0]
    # 4) 标题关键词
    _title = (scenes.get(script) or {}).get("title") or ""
    for rx, arc in ARC_KW:
        if rx.search(_title):
            return arc
    # 5) 攻略日期
    st = STIME.get(script)
    if st and st[0] and st[1]:
        a = arc_of_date(st[0], st[1])
        if a:
            return a
    rf = REFTIME.get(script)
    if rf:
        a = arc_of_date(rf[0], rf[1])
        if a:
            return a
    return "不限时间"


'''
s = s[:start] + new_fn + s[end:]
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("arc_of 重写：人工 > 章节 > 关键词 > 日期")
