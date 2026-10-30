# -*- coding: utf-8 -*-
"""地点筛选改成现实地理区域（一级），类型降为第二排筛选。

区域口径按现实地理：
  川蜀（四川盆地）、巴渝（重庆）、荆湖（湖北湖南）、两浙淮南（江浙皖）、
  中原（河南）、关中陇右（陕甘）、西南夷（云贵）、闽越（福建）、
  塞外（北方）、海外、其他（虚构或无法定位）
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"

REGION_MAP = {
    "成都": "川蜀", "眉山": "川蜀", "绵州": "川蜀", "绵阳": "川蜀", "梓州": "川蜀",
    "乐山": "川蜀", "青城山": "川蜀", "峨嵋山": "川蜀", "剑门关": "川蜀", "昭化": "川蜀",
    "唐门": "川蜀", "岷江": "川蜀", "渡口": "川蜀", "泸沽湖": "川蜀", "大雪山": "川蜀",
    "剑庐": "川蜀", "剑圣故居": "川蜀",
    "夔州": "巴渝", "夔门": "巴渝", "白帝城遗迹": "巴渝", "朝天门": "巴渝",
    "江陵": "荆湖", "荆州": "荆湖", "襄阳": "荆湖", "枣阳": "荆湖", "岳阳": "荆湖",
    "长沙雨花亭": "荆湖", "静江": "荆湖", "风雨山": "荆湖", "锦香宫": "荆湖",
    "临安": "两浙淮南", "建康": "两浙淮南", "宣州孤云山": "两浙淮南",
    "宁国府": "两浙淮南", "安济坊": "两浙淮南",
    "汴京": "中原", "朱仙镇": "中原", "嵩山": "中原", "南嵩山寺": "中原",
    "南阳": "中原", "新野": "中原", "南阳杏花林": "中原",
    "华山": "关中陇右", "终南山": "关中陇右", "平凉": "关中陇右", "崆峒山": "关中陇右",
    "秦州": "关中陇右", "兴元府": "关中陇右", "西和州": "关中陇右",
    "大理": "西南夷", "点苍山": "西南夷", "天龙寺": "西南夷", "矩州": "西南夷",
    "福州": "闽越",
    "阴山": "塞外", "天山": "塞外", "长白山": "塞外", "金国": "塞外",
    "东瀛": "海外",
}
PREFIX_REGION = (("唐门", "川蜀"), ("青城", "川蜀"), ("崆峒", "关中陇右"),
                 ("江陵", "荆湖"), ("锦香宫", "荆湖"))

helper = '''

REGION_MAP = %r
PREFIX_REGION = %r


def _region_of(nm):
    n = nm or ""
    if n in REGION_MAP:
        return REGION_MAP[n]
    for pre, reg in PREFIX_REGION:
        if n.startswith(pre):
            return reg
    return "其他"

''' % (REGION_MAP, PREFIX_REGION)

P = B + r"\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()
if "_region_of" not in s:
    s = s.replace("\n\ndef _faction_type(", helper + "\ndef _faction_type(", 1)
old = "            _f1 = _place_type(_nm, _lead)"
new = "            _f1 = _region_of(_nm)\n            _f2 = _place_type(_nm, _lead)"
assert old in s, "地点 facet 行未找到"
s = s.replace(old, new)
open(P, "w", encoding="utf-8").write(s)
print("build_wiki2：地点一级筛选=区域，二级=类型")

H = B + r"\web\wiki.html"
h = open(H, encoding="utf-8").read()
h = h.replace("'地点':'类型'", "'地点':'区域'")
h = h.replace("const FACET_LABEL={", "const FACET2_LABEL={'事件':'主线','地点':'类型'};\nconst FACET_LABEL={")
h = h.replace('<span class="clbl">主线</span>', '<span class="clbl">${esc(FACET2_LABEL[type]||\'分类\')}</span>')
open(H, "w", encoding="utf-8").write(h)
print("wiki.html：筛选标题改为 区域 / 类型")
