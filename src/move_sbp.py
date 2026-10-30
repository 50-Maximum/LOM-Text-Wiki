# -*- coding: utf-8 -*-
"""把「地点-场景索引」挪到 scenes 载入之后（之前放在前面，scenes 还不存在）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

block = '''
# 地点 → 场景（按 place_of 反查，供地点页「发生场景」栏）
SCENES_BY_PLACE = {}
for _s7 in list(scenes):
    try:
        _p7, _e7 = place_of(_s7)
    except Exception:
        continue
    if _p7:
        SCENES_BY_PLACE.setdefault(_p7, []).append(_s7)
print("地点-场景索引", len(SCENES_BY_PLACE), "个地点 /",
      sum(len(v) for v in SCENES_BY_PLACE.values()), "场")
'''
if block in s:
    s = s.replace(block, "", 1)
    print("已移除前置块")

anchor = ('scenes = {r[0]: {"title": r[1], "chapter": r[2], "lines": r[3], "place": r[4]}\n'
          '          for r in c.execute("select script,title,chapter,line_count,place from scenes")}\n')
assert anchor in s, "scenes 定义未找到"
if "SCENES_BY_PLACE = {}" not in s.split(anchor)[1][:200]:
    s = s.replace(anchor, anchor + block, 1)
    print("已插入 scenes 之后")

open(S, "w", encoding="utf-8").write(s)
print("done")
