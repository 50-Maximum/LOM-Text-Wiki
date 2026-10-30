# -*- coding: utf-8 -*-
"""修 extra_persons 分支的写死模板（改为优先用人工导语）；？？？ 改名无名角色。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"

s = open(p, encoding="utf-8").read().replace("\r\n", "\n")
old = ('            _lead = "%s，原文中出现 %d 处，未给出成段的人物介绍，以下为原文摘录。" % (_nm, _tot)')
new = ('            _lead = ((intro_of(_slug) or {}).get("text")\n'
       '                     or "%s，原文中出现 %d 处。" % (_nm, _tot))')
if old in s:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("extra_persons 导语改为优先人工")
else:
    print("未找到该模板行（可能已改）")

cf = json.load(open(os.path.join(B, "chars_fix.json"), encoding="utf-8"))
cf.setdefault("merge", {})["？？？"] = "无名角色"
json.dump(cf, open(os.path.join(B, "chars_fix.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("并义 ？？？ → 无名角色")

ic = json.load(open(os.path.join(B, "intros_char.json"), encoding="utf-8"))
ic["人物/无名角色"] = {
    "text": "这一页收的是原文里只标了「？？？」、没有留下姓名的说话人。"
            "全剧共 206 句、分布在 85 个场景，其中绝大多数其实认得出是谁："
            "紧接的下一句往往就点名或自报家门，例如龙渊、唐布衣、瑞笙、夏侯兰、瑞杏、叶云裳、"
            "石公远、方震天、金乌上人、虞小梅等人。判明归属的已归回各人条目，"
            "这里只留确实无名的少数：斥申屠龙「邪魔歪道」的冤魂、偷衣的同门、"
            "指控唐布衣的无名女子、撞人的顽童、鬼卒、山贼与几处群体。",
    "footnotes": [],
}
json.dump(ic, open(os.path.join(B, "intros_char.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("无名角色 导语已写")
