# -*- coding: utf-8 -*-
"""第 7 批修补：城池认定、上级字段补全、青城山镇去重、补回岳阳。"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

# ① place_edits 增补
p = os.path.join(BASE, "data", "place_edits.json")
E = json.load(open(p, encoding="utf-8"))
E.setdefault("rename", {})["青城-青城山镇"] = "青城山镇"
names = {x.get("name") for x in E.get("new_places") or []}
if "岳阳" not in names:
    E.setdefault("new_places", []).append(
        {"name": "岳阳", "parent": "", "lead": "岳阳是荆湖重镇，风雨山、锦香宫皆在其境。"})
json.dump(E, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("place_edits 增补完成")

S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()

# ② 类型：补城池名录与后缀
if "CITY_NAMES" not in s:
    old = 'def _place_type2(nm, lead="", parent=""):\n    """地点类型（外层筛选）：按名字后缀 + 上级语境判定。"""\n    n = nm or ""\n    base = n.split("-")[-1]'
    new = ('CITY_NAMES = {"临安", "建康", "汴京", "江陵", "襄阳", "南阳", "平凉", "大理",\n'
           '              "昭化", "枣阳", "新野", "成都", "绵州", "夔州", "兴元府", "眉山",\n'
           '              "长沙", "岳阳", "静江", "岳州", "鄂州", "潭州"}\n\n\n'
           'def _place_type2(nm, lead="", parent=""):\n'
           '    """地点类型（外层筛选）：按名字后缀 + 城池名录判定。"""\n'
           '    n = nm or ""\n    base = n.split("-")[-1]\n'
           '    if base in CITY_NAMES:\n        return "城池"')
    assert old in s, "_place_type2 头未找到"
    s = s.replace(old, new, 1)

old_suf = ('    if base.endswith(("山", "峰", "岭", "河", "江", "湖", "泉", "池", "峡", "洞",\n'
           '                      "谷", "溪", "林", "森林", "崖", "滩")):\n        return "山川"')
new_suf = ('    if base.endswith(("山", "峰", "岭", "河", "江", "湖", "泉", "池", "峡", "洞",\n'
           '                      "谷", "溪", "林", "森林", "崖", "滩", "岗", "坡", "岛",\n'
           '                      "沱", "洲", "潭", "原")):\n        return "山川"')
if old_suf in s:
    s = s.replace(old_suf, new_suf, 1)
    print("类型后缀已扩充")

old_shop = '    if base.endswith(("楼", "铺", "舖", "摊", "巷", "阁", "肆", "客栈", "栈", "市", "集")):\n        return "街市店肆"'
new_shop = '    if base.endswith(("楼", "铺", "舖", "摊", "巷", "阁", "肆", "客栈", "栈", "市", "集",\n                      "店", "馆", "堂", "坊")):\n        return "街市店肆"'
if old_shop in s:
    s = s.replace(old_shop, new_shop, 1)
    print("店铺后缀已扩充")

# ③ 收尾：子级缺上级的补上
if "_FIX_PARENT_INF" not in s:
    anchor = 'print("导语补注", len(PE_TIP), "处；隐藏", len(PE_HIDE), "个区域页")'
    assert anchor in s
    add = anchor + '''

# 子级页面补齐「上级」字段（有些页由 extra/占位分支生成，没带上级）
_FIX_PARENT_INF = 0
for _i5, _q5 in enumerate(pages):
    if _q5[1] != "地点":
        continue
    _nm5 = _q5[2]
    _par5 = PPARENT.get(_nm5)
    if not _par5:
        continue
    _inf5 = _pj(_q5[4], "{}")
    if _inf5.get("上级") == _par5:
        continue
    _inf5["上级"] = _par5
    pages[_i5] = (_q5[0], _q5[1], _q5[2], _q5[3],
                  json.dumps(_inf5, ensure_ascii=False), _q5[5], _q5[6], _q5[7],
                  _q5[8], _q5[9], _q5[10], _q5[11], _q5[12], _q5[13])
    _FIX_PARENT_INF += 1
if _FIX_PARENT_INF:
    print("补上级字段", _FIX_PARENT_INF, "页")
'''
    s = s.replace(anchor, add, 1)
    print("已加上级补全")

open(S, "w", encoding="utf-8").write(s)
print("patch 完成")
