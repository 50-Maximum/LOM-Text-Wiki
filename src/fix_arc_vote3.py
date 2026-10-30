# -*- coding: utf-8 -*-
"""投票收紧第二版：至少两类信号（地点/人物/情节）同时支持，且总分≥5。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

start = s.index("def arc_vote(script):")
end = s.index("def arc_of(script):")
new_fn = '''def arc_vote(script):
    """按地点、参与人物、标题情节投票；需≥两类信号且总分≥5。"""
    _info = scenes.get(script) or {}
    _pl = _info.get("place") or ""
    _ti = _info.get("title") or ""
    _sps = [r[0] for r in c.execute(
        "select distinct speaker from lines where script=? and speaker<>''", (script,))]
    _score = collections.Counter()
    _kinds = collections.Counter()
    for _a in ARC_ORDER:
        if _a == "不限时间":
            continue
        _s, _k = 0, 0
        if _pl and _pl in ARC_PLACE.get(_a, ()):
            _s += 3
            _k += 1
        _hit = sum(1 for _x in _sps if _x in ARC_PERSON.get(_a, ()))
        if _hit:
            _s += min(_hit, 3)
            _k += 1
        for _rx, _arc2 in ARC_KW:
            if _arc2 == _a and _rx.search(_ti):
                _s += 2
                _k += 1
                break
        if _s:
            _score[_a] = _s
            _kinds[_a] = _k
    if not _score:
        return ""
    _best = max(_score.values())
    for _a in ARC_ORDER:
        if _score.get(_a) == _best and _best >= 5 and _kinds.get(_a, 0) >= 2:
            return _a
    return ""


'''
s = s[:start] + new_fn + s[end:]
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("投票收紧：需≥2 类信号且 ≥5 分")
