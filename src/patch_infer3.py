# -*- coding: utf-8 -*-
"""过滤掉没有对应地点页的推断（如「途中」），再接入 place_of。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
have = {r[0] for r in c.execute("select name from pages where type='地点'")}
p = os.path.join(BASE, "data", "place_infer3.json")
D = json.load(open(p, encoding="utf-8"))
keep = {k: v for k, v in D.items() if v.get("place") in have}
drop = len(D) - len(keep)
json.dump(keep, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("保留 %d 条，剔除 %d 条（地点页不存在）" % (len(keep), drop))
if drop:
    bad = sorted({v["place"] for k, v in D.items() if v.get("place") not in have})
    print("被剔除的地点名:", bad)

S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()
if "PLACE_INFER3" not in s:
    anchor = 'PLACE_INFER2 = {}'
    idx = s.find(anchor)
    assert idx > 0
    end = s.find("PLACE_INFER2 = {}", idx)  # noqa
    block_end = s.find("\n\n", s.find('PLACE_INFER2 = json.load', idx))
    add = '''
PLACE_INFER3 = {}
try:
    _pi3 = os.path.join(BASE, "data", "place_infer3.json")
    if os.path.exists(_pi3):
        PLACE_INFER3 = json.load(open(_pi3, encoding="utf-8"))
except Exception:
    PLACE_INFER3 = {}'''
    # 插到 PLACE_INFER2 载入块之后
    pos = s.find("PLACE_INFER2 = {}", idx)
    pos2 = s.find("\n\n", s.find("except Exception:\n    PLACE_INFER2 = {}", idx))
    s = s[:pos2] + add + s[pos2:]
    print("已加载 PLACE_INFER3")

if "PLACE_INFER3.get(script)" not in s:
    tail = '    _i2 = PLACE_INFER2.get(script) or {}'
    assert tail in s
    ins = '''    _i3 = PLACE_INFER3.get(script) or {}
    if _i3.get("place"):
        return pcanon(_i3["place"]), (_i3.get("src") or "承前场（推断）")
'''
    s = s.replace(tail, ins + tail, 1)
    print("place_of 已接链式推断")

open(S, "w", encoding="utf-8").write(s)
print("done")
