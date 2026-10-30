# -*- coding: utf-8 -*-
"""第 7 批地点改订 + 地点类型重构。"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
p = os.path.join(BASE, "data", "place_edits.json")
E = json.load(open(p, encoding="utf-8"))

E.setdefault("rename", {}).update({
    "剑圣故居": "剑庐",
    "绵阳": "绵州",
    "谭州腾云山": "腾云寨",
    "红岭": "新野",
    "成都": "川蜀",
})
E.setdefault("delete", [])
for d in ("山神龛", "金国"):
    if d not in E["delete"]:
        E["delete"].append(d)
E.setdefault("parent", {}).update({
    "青城山镇": "青城山",
    "黄龙泉": "崆峒山",
    "剑庐": "点苍山",
    "夔州巫山县衙大牢": "夔州",
    "夔门": "夔州",
    "白帝城遗迹": "夔州",
    "朽木桥": "崆峒山",
    "孟章厢房": "崆峒山",
    "陵光厢房": "崆峒山",
    "插香台": "崆峒山",
    "监兵厢房": "崆峒山",
    "香露池": "锦香宫",
    "春雨楼": "江陵",
    "锦绣轩": "锦香宫",
    "般若院": "嵩山",
    "松烟阁": "点苍山",
})
E["top_level"] = ["锦香宫", "风雨山", "腾云寨"]
E.setdefault("region", {}).update({"兴元府": "川蜀", "南嵩山寺": "其他"})
E.setdefault("tips", {})
E["tips"]["腾云寨"] = ("（校订：腾云寨在游戏开局时已成覆灭之地，昔日石帮主据此为寇；"
                     "寨在谭州腾云山上。）")
E["tips"]["剑庐"] = "（原名剑圣故居，同一处。）"
# 区域改名：西南夷 → 西南
E["region_rename"] = {"西南夷": "西南"}
json.dump(E, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("place_edits 已更新")

S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()

# ① top_level 去掉上级
if "PE_TOP" not in s:
    anchor = 'PE_HIDE = set(PE.get("hide") or [])'
    assert anchor in s
    s = s.replace(anchor, anchor + '\nPE_TOP = PE.get("top_level") or []\n'
                  'PE_RENAME = PE.get("region_rename") or {}', 1)
    open(S, "w", encoding="utf-8").write(s)
    print("已加 PE_TOP / PE_RENAME 变量")

s = open(S, encoding="utf-8").read()
if 'for _t3 in PE_TOP:' not in s:
    anchor2 = 'for _k2, _v2 in (PE.get("parent") or {}).items():\n    PPARENT[_k2] = _v2'
    assert anchor2 in s
    s = s.replace(anchor2, anchor2 + '\nfor _t3 in PE_TOP:\n    PPARENT.pop(_t3, None)', 1)
    print("已加 top_level 处理")

# ② 区域改名
if 'PE_RENAME.get(r' not in s:
    old = ('    r = _region_of0(nm)\n'
           '    if r == "巴渝":          # 巴渝并入川蜀\n'
           '        r = "川蜀"\n'
           '    return PE_REGION.get(nm, r)')
    new = ('    r = _region_of0(nm)\n'
           '    if r == "巴渝":          # 巴渝并入川蜀\n'
           '        r = "川蜀"\n'
           '    r = PE_RENAME.get(r, r)\n'
           '    return PE_REGION.get(nm, r)')
    assert old in s, "_region_of wrapper 未找到"
    s = s.replace(old, new, 1)
    print("已加区域改名")

# ③ 地点类型重构
if "def _place_type2(" not in s:
    fn = '''

def _place_type2(nm, lead="", parent=""):
    """地点类型（外层筛选）：按名字后缀 + 上级语境判定。"""
    n = nm or ""
    base = n.split("-")[-1]
    if base.endswith(("遗迹", "故居", "旧址", "遗址")):
        return "遗迹"
    if base.endswith(("大牢", "牢房", "狱", "牢")):
        return "牢狱"
    if base.endswith(("寺", "观", "庵", "祠", "庙")):
        return "寺院宫观"
    if base.endswith(("楼", "铺", "舖", "摊", "巷", "阁", "肆", "客栈", "栈", "市", "集")):
        return "街市店肆"
    if base.endswith(("关", "渡", "桥", "寨", "隘", "津", "门", "口")):
        return "关隘渡口"
    if base.endswith(("村", "镇", "乡", "庄")):
        return "村镇乡野"
    if base.endswith(("山", "峰", "岭", "河", "江", "湖", "泉", "池", "峡", "洞",
                      "谷", "溪", "林", "森林", "崖", "滩")):
        return "山川"
    if base.endswith(("府", "州", "县", "城", "郡")):
        return "城池"
    if base.endswith(("堂", "殿", "场", "房", "院", "阁楼", "宫")) or parent:
        return "门派驻地"
    return "其他"

'''
    marker = "\ndef _faction_type(nm):"
    assert marker in s
    s = s.replace(marker, fn + marker, 1)
    print("已加 _place_type2")

if "_place_type2(_nm, _lead" not in s:
    s = s.replace("_f2 = _place_type(_nm, _lead)",
                  "_f2 = _place_type2(_nm, _lead, PPARENT.get(_nm))", 1)
    print("类型判定已切到 _place_type2")

open(S, "w", encoding="utf-8").write(s)
print("build_wiki2 补丁完成")
