# -*- coding: utf-8 -*-
"""事件层第一轮修复：阶段顺序、阶段判定、选项可点、参数中文化、备注卫生。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 1) 阶段顺序 + 映射
arcs = load("arcs.json")
arcs["arcs"] = ["外姓弟子", "南宫寿宴", "江陵围城", "唐门衰败", "武林大会",
                "比武招亲", "武林盟进攻唐门", "不限时间"]
arcs["chapter_map"]["其他"] = ""
sc = arcs.setdefault("scene", {})
sc.update({
    "meeting_option_705_01": "唐门衰败",
    "S8400_01": "外姓弟子",
    "S8400_01_01": "江陵围城",
    "travel_result_401_501": "不限时间",
    "travel_result_401_504": "不限时间",
    "S9903_01": "外姓弟子",
})
save("arcs.json", arcs)
print("阶段顺序已改为：外姓弟子→南宫寿宴→江陵围城→唐门衰败→武林大会→比武招亲→武林盟进攻唐门")

# 2) 参数中文化表
stat = {
    "karma": "因果", "disposition": "性情", "mental": "心相", "fame": "名声",
    "reputation": "声望", "money": "银两", "health": "气血", "life": "寿命",
    "attack": "攻击", "defence": "防御", "defense": "防御", "agility": "身法",
    "internal": "内力", "poison": "毒术", "medicine": "医术", "charm": "魅力",
}
save("stat_names.json", stat)
print("参数中文表写入 %d 条" % len(stat))

s = open(P, encoding="utf-8").read().replace("\r\n", "\n")

# 3) 载入中文表 + 备注过滤
if "STAT_NAMES" not in s:
    anchor = "def char_prefix(nm):"
    blk = ('# 参数中文名（data/stat_names.json）\n'
           'STAT_NAMES = {}\n'
           'try:\n'
           '    _snp = os.path.join(BASE, "data", "stat_names.json")\n'
           '    if os.path.exists(_snp):\n'
           '        STAT_NAMES = json.load(open(_snp, encoding="utf-8"))\n'
           'except Exception:\n'
           '    STAT_NAMES = {}\n\n\n'
           'def stat_cn(txt):\n'
           '    if not txt:\n'
           '        return txt\n'
           '    out = txt\n'
           '    for k, v in STAT_NAMES.items():\n'
           '        out = out.replace(k, v)\n'
           '    return out\n\n\n')
    s = s.replace(anchor, blk + anchor, 1)
    print("已插入 STAT_NAMES/stat_cn")

# 4) 选项行：显示中文参数、标题换成场景名、可点
old = '''                if _o.get("effects"):
                    _note += "　影响：" + "、".join(_o["effects"])'''
new = '''                if _o.get("effects"):
                    _note += "　影响：" + stat_cn("、".join(_o["effects"]))'''
s = s.replace(old, new, 1)

old2 = '''                _brows.append({"note": _note, "quote": "", "script": _tgt,
                               "title": _tgt, "seq": 0, "routes": []})'''
new2 = '''                _brows.append({"note": _note, "quote": "",
                               "script": _tgt,
                               "title": ((scenes.get(_tgt) or {}).get("title") or _tgt) if _tgt else "",
                               "seq": 0, "routes": []})'''
if old2 in s:
    s = s.replace(old2, new2, 1)
    print("选项行改为按场景名链接")

open(P, "w", encoding="utf-8", newline="\n").write(s)
print("build_wiki2.py 已更新")
