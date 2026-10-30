# -*- coding: utf-8 -*-
"""投票收紧：只采信「高度集中于某一阶段」的地点与人物（≥60%），避免赵活/唐门这种通杀信号。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

start = s.index("# ---------- 阶段特征：地点 / 人物 指纹")
end = s.index("def arc_vote(script):")

new_blk = '''# ---------- 阶段特征：只取「高度集中」的地点与人物（占比≥60%） ----------
ARC_PLACE = {}
ARC_PERSON = {}
try:
    _pc = collections.defaultdict(collections.Counter)
    _uc = collections.defaultdict(collections.Counter)
    for _sc0, _info0 in scenes.items():
        _ch0 = _info0.get("chapter") or ""
        if _ch0 in ("支线", "其他", "角色线"):
            continue
        _a0 = ARC_CH.get(_ch0)
        if not _a0:
            continue
        _pl0 = _info0.get("place") or ""
        if _pl0:
            _pc[_pl0][_a0] += 1
    for _sc0, _sp0, _n0 in c.execute(
            "select script,speaker,count(*) from lines where speaker<>'' group by script,speaker"):
        _ch0 = (scenes.get(_sc0) or {}).get("chapter") or ""
        if _ch0 in ("支线", "其他", "角色线"):
            continue
        _a0 = ARC_CH.get(_ch0)
        if not _a0:
            continue
        _uc[_sp0][_a0] += _n0

    for _pl0, _cc in _pc.items():
        _tot = sum(_cc.values())
        _top, _n = _cc.most_common(1)[0]
        if _tot >= 3 and _n / _tot >= 0.6:
            ARC_PLACE.setdefault(_top, set()).add(_pl0)
    for _sp0, _cc in _uc.items():
        _tot = sum(_cc.values())
        _top, _n = _cc.most_common(1)[0]
        if _tot >= 4 and _n / _tot >= 0.6:
            ARC_PERSON.setdefault(_top, set()).add(_sp0)
    print("阶段指纹（集中度≥60%%）：地点 %d 条，人物 %d 条"
          % (sum(len(v) for v in ARC_PLACE.values()), sum(len(v) for v in ARC_PERSON.values())))
except Exception as _e:
    print("阶段指纹跳过:", _e)


'''
s = s[:start] + new_blk + s[end:]

# 投票阈值提高
s = s.replace('''        if _s:
            _score[_a] = _s''', '''        if _s >= 3:
            _score[_a] = _s''', 1)
s = s.replace('''    if _best < 3:
        return ""''', '''    if _best < 4:
        return ""''', 1)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("指纹改为集中度筛选，阈值提高")
