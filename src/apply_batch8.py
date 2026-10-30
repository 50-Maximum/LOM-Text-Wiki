# -*- coding: utf-8 -*-
"""第 8 批：改名腾云山、取消三类、福建做子级、简介整段重写（不加括号）。"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
p = os.path.join(BASE, "data", "place_edits.json")
E = json.load(open(p, encoding="utf-8"))

# 1) 改名：腾云寨 → 腾云山
E.setdefault("rename", {}).pop("腾云寨", None)
E["rename"]["腾云寨"] = "腾云山"

# 2) 只保留你点名要的修订者留言（临镇），其余括号注释全部撤掉
E["tips"] = {k: v for k, v in (E.get("tips") or {}).items() if k == "临镇"}

# 3) 简介整段重写
E["intro"] = {
    "腾云山": "腾云山在谭州境内，石帮主昔日在此落草为寇，所据山寨即腾云寨。腾云寨建在腾云山上，山下有寨门与哨道相连。游戏开局时腾云寨已经覆灭：石帮主之父曾率兵围剿，假意拿钱赎人，实则带人放火烧山，寨众就此溃散。",
    "烟花阁": "烟花阁是江陵的风尘之地，与花月楼同类。唐布衣曾向赵活称它是神秘组织并点出名号，唐铮听闻当即怒斥；所谓神秘组织只是唐布衣胡诌，别无实据。现有笔记未记载其成员、据点或与主线的进一步关联。",
    "画舫": "画舫是江上供人听曲饮酒的船家场所，谭霸刀每日上画舫听曲喝酒，唐布衣据此告诉众人上船便能找到他。舫上有女乐侍奉；唐铮曾在舫上所用合香中下毒，女乐自称也是头一次闻见，并非舫家一向如此。",
    "野狐桥": "野狐桥是一处与金乌上人遇袭相关的地点。金乌上人行经野狐桥时，被人从背后推了一把，跌落一线天。",
    "朱家葱肉包摊": "朱家葱肉包摊是朱婶经营的包子摊，葱肉包子一颗卖十文钱。赵活曾来此买包子，随后发现被骗。此处本是卧云岗的摊子；若完成大师兄交代的关照摊子一事，摊子其后会迁到唐门外堡。",
    "栖霞太虚观": "栖霞太虚观是丘处机的故居，属登州蓬莱县阳疃镇。唐升曾向人提起此处，说二十年前丘处机曾与弟子在此修道，正因如此，丘处机未参与极乐教与中原正派之战。",
}

# 4) 上级：上官交引舖 → 福建；烟花阁 → 江陵
E.setdefault("parent", {}).update({"上官交引舖": "福建", "烟花阁": "江陵"})

# 5) 新增福建
names = {x.get("name") for x in E.get("new_places") or []}
if "福建" not in names:
    E.setdefault("new_places", []).append(
        {"name": "福建", "parent": "", "lead": "福建是东南沿海的州县之地，福州、上官交引舖皆在其境。"})

# 6) 类型：取消关隘渡口/门派驻地/村镇乡野，按名指定
E["type"] = {
    "锦香宫": "山川", "剑门关": "山川", "腾云山": "山川", "渡口": "山川",
    "岳阳": "城池", "朱仙镇": "城池",
    "唐门": "其他", "青城山镇": "其他", "眉山镇": "其他", "崆峒山村": "其他",
    "临镇": "其他", "野狐桥": "其他",
}
json.dump(E, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("place_edits 更新完成")

S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()

# 7) 重写 _place_type2
i = s.find("def _place_type2(")
j = s.find("\ndef _faction_type(", i)
assert i > 0 and j > i
new_fn = '''def _place_type2(nm, lead="", parent=""):
    """地点类型：城池 / 山川 / 街市店肆 / 寺院宫观 / 遗迹 / 牢狱 / 其他。"""
    n = nm or ""
    base = n.split("-")[-1]
    if base in PE_TYPE:
        return PE_TYPE[base]
    if base.endswith(("遗迹", "故居", "旧址", "遗址")):
        return "遗迹"
    if base.endswith(("大牢", "牢房", "狱", "牢")):
        return "牢狱"
    if base.endswith(("寺", "观", "庵", "祠", "庙")):
        return "寺院宫观"
    if base in CITY_NAMES or base.endswith(("府", "州", "县", "城", "郡", "镇")):
        return "城池"
    if base.endswith(("山", "峰", "岭", "河", "江", "湖", "泉", "池", "峡", "洞",
                      "谷", "溪", "林", "森林", "崖", "滩", "岗", "坡", "岛",
                      "沱", "洲", "潭", "原", "关", "渡", "口")):
        return "山川"
    if base.endswith(("楼", "铺", "舖", "摊", "巷", "阁", "肆", "客栈", "栈",
                      "市", "集", "店", "馆", "堂", "坊")):
        return "街市店肆"
    return "其他"

'''
s = s[:i] + new_fn + s[j + 1:]

# 8) PE_TYPE / PE_INTRO 变量 + 简介覆盖
if "PE_TYPE" not in s:
    anchor = 'PE_RENAME = PE.get("region_rename") or {}'
    assert anchor in s
    s = s.replace(anchor, anchor + '\nPE_TYPE = PE.get("type") or {}\nPE_INTRO = PE.get("intro") or {}', 1)

if "_INTRO_APPLIED" not in s:
    anchor2 = 'print("补上级字段", _FIX_PARENT_INF, "页")'
    assert anchor2 in s
    add2 = anchor2 + '''

# 简介整段覆盖（人工重写，不加括号注释）
_INTRO_APPLIED = 0
for _i6, _q6 in enumerate(pages):
    if _q6[1] != "地点":
        continue
    _new_lead = PE_INTRO.get(_q6[2])
    if _new_lead and _new_lead != _q6[3]:
        pages[_i6] = (_q6[0], _q6[1], _q6[2], _new_lead, _q6[4], _q6[5], _q6[6],
                      _q6[7], _q6[8], _q6[9], _q6[10], _q6[11], _q6[12], _q6[13])
        _INTRO_APPLIED += 1
if _INTRO_APPLIED:
    print("简介重写", _INTRO_APPLIED, "条")
'''
    s = s.replace(anchor2, add2, 1)

open(S, "w", encoding="utf-8").write(s)
print("build_wiki2 补丁完成")
