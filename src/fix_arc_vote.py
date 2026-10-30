# -*- coding: utf-8 -*-
"""阶段判定加投票：章节、地点、参与人物、标题情节、日期各计权重。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

start = s.index("def arc_of(script):")
end = s.index("for _s, _v in scenes.items():")

new_fn = '''# ---------- 阶段特征：地点 / 人物 指纹（只从章节明确的场景里学） ----------
ARC_PLACE = {}
ARC_PERSON = {}
try:
    _pc = {a: collections.Counter() for a in ARC_ORDER}
    _uc = {a: collections.Counter() for a in ARC_ORDER}
    for _sc0, _info0 in scenes.items():
        _ch0 = _info0.get("chapter") or ""
        if _ch0 in ("支线", "其他", "角色线"):
            continue
        _a0 = ARC_CH.get(_ch0)
        if not _a0:
            continue
        _pl0 = _info0.get("place") or ""
        if _pl0:
            _pc.setdefault(_a0, collections.Counter())[_pl0] += 1
    for _sc0, _sp0, _n0 in c.execute(
            "select script,speaker,count(*) from lines where speaker<>'' group by script,speaker"):
        _ch0 = (scenes.get(_sc0) or {}).get("chapter") or ""
        if _ch0 in ("支线", "其他", "角色线"):
            continue
        _a0 = ARC_CH.get(_ch0)
        if not _a0:
            continue
        _uc.setdefault(_a0, collections.Counter())[_sp0] += _n0
    ARC_PLACE = {a: {k for k, v in cc.items() if v >= 2} for a, cc in _pc.items()}
    ARC_PERSON = {a: {k for k, v in cc.items() if v >= 6} for a, cc in _uc.items()}
    print("阶段指纹：地点 %d 段，人物 %d 段"
          % (len([1 for v in ARC_PLACE.values() if v]), len([1 for v in ARC_PERSON.values() if v])))
except Exception as _e:
    print("阶段指纹跳过:", _e)


def arc_vote(script):
    """按地点、参与人物、标题情节投票，返回最高分阶段（同分取阶段序靠前）。"""
    _info = scenes.get(script) or {}
    _pl = _info.get("place") or ""
    _ti = _info.get("title") or ""
    _sps = [r[0] for r in c.execute(
        "select distinct speaker from lines where script=? and speaker<>''", (script,))]
    _score = collections.Counter()
    for _a in ARC_ORDER:
        if _a == "不限时间":
            continue
        _s = 0
        if _pl and _pl in ARC_PLACE.get(_a, ()):
            _s += 3
        _hit = sum(1 for _x in _sps if _x in ARC_PERSON.get(_a, ()))
        _s += min(_hit, 3)
        for _rx, _arc2 in ARC_KW:
            if _arc2 == _a and _rx.search(_ti):
                _s += 2
                break
        if _s:
            _score[_a] = _s
    if not _score:
        return ""
    _best = max(_score.values())
    if _best < 3:
        return ""
    for _a in ARC_ORDER:
        if _score.get(_a) == _best:
            return _a
    return ""


def arc_of(script):
    # 1) 人工指定
    if script in ARC_SC:
        return ARC_SC[script]
    _ch0 = (scenes.get(script) or {}).get("chapter") or ""
    # 2) 正章：章节即归属
    if _ch0 in ARC_CH and ARC_CH[_ch0] and _ch0 not in ("支线", "其他", "角色线"):
        return ARC_CH[_ch0]
    # 3) 支线/其他：先投票（地点/人物/情节）
    _v = arc_vote(script)
    if _v:
        return _v
    # 4) 攻略日期
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
print("arc_of 已加入地点/人物/情节投票")
