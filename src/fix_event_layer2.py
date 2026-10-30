# -*- coding: utf-8 -*-
"""事件层第二轮：笔记文本覆盖、第0章归武林盟进攻唐门、过滤攻略「备注」噪声。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 1) 第0章 = 武林盟进攻唐门的序章
arcs = load("arcs.json")
arcs["chapter_map"]["第0章"] = "武林盟进攻唐门"
arcs.setdefault("scene", {})["ch0_5"] = "武林盟进攻唐门"
save("arcs.json", arcs)
print("第0章 → 武林盟进攻唐门；ch0_5 同步")

# 2) 笔记文本覆盖
patch = load("notes_patch.json")
patch.setdefault("travel_result_401_501", {})["三人道中遇敌拦路"] = {
    "note": "唐布衣等三人行路时遭人持兵刃袭击。龙湘与福韫二人中择一出战，不是先后各打一场。"}
patch.setdefault("travel_result_401_504", {})["三人道中遇敌拦路"] = {
    "note": "三人行于道中遭敌人拦路索命。龙湘与福韫二人中择一出战，另一人不出手。"}
save("notes_patch.json", patch)
print("两处「先后出手」已改为二择一")

s = open(P, encoding="utf-8").read().replace("\r\n", "\n")

# 3) 应用笔记补丁
if "NOTE_PATCH" not in s:
    anchor = "print(\"笔记\", len(notes))"
    blk = (anchor + "\n\n"
           "# 人工笔记覆盖（data/notes_patch.json）\n"
           "NOTE_PATCH = {}\n"
           "try:\n"
           "    _npp = os.path.join(BASE, \"data\", \"notes_patch.json\")\n"
           "    if os.path.exists(_npp):\n"
           "        NOTE_PATCH = json.load(open(_npp, encoding=\"utf-8\"))\n"
           "except Exception as _e:\n"
           "    print(\"笔记补丁跳过:\", _e)\n"
           "if NOTE_PATCH:\n"
           "    _n2 = []\n"
           "    for _row in notes:\n"
           "        _sc, _a, _b, _t, _nm, _no, _q = _row\n"
           "        _pv = (NOTE_PATCH.get(_sc) or {}).get(_nm)\n"
           "        if _pv:\n"
           "            if _pv.get(\"drop\"):\n"
           "                continue\n"
           "            _no = _pv.get(\"note\", _no)\n"
           "            if _pv.get(\"name\"):\n"
           "                _nm = _pv[\"name\"]\n"
           "        _n2.append((_sc, _a, _b, _t, _nm, _no, _q))\n"
           "    notes = _n2\n"
           "    print(\"笔记补丁后\", len(notes))\n")
    s = s.replace(anchor, blk, 1)
    print("已插入 NOTE_PATCH")

# 4) 触发条件里过滤攻略噪声（备注/差分/影响…）
old = '''            secs.insert(0, {"h": "触发条件", "rows": _crow2[:16]})'''
new = '''            _crow2 = [r for r in _crow2
                      if not re.match(r"^\\s*备注[:：]", (r.get("note") or ""))
                      and "差分" not in (r.get("note") or "")
                      and "第三年" not in (r.get("note") or "")]
            if _crow2:
                secs.insert(0, {"h": "触发条件", "rows": _crow2[:16]})'''
if old in s:
    s = s.replace(old, new, 1)
    print("触发条件已过滤备注/差分噪声")

open(P, "w", encoding="utf-8", newline="\n").write(s)
print("build_wiki2.py 已更新")
