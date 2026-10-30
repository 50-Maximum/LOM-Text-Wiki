# -*- coding: utf-8 -*-
"""修地名前缀错位（崆峒山-X → 崆峒-X，页面上只有崆峒-X），并落第 5 批：夺魄门场景细分驻地。"""
import io, json, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

# 1) pcanon 里补前缀归一
S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()
if '"崆峒-"' not in s:
    old = '    n = PMERGE.get(n, n)\n'
    new = ('    n = PMERGE.get(n, n)\n'
           '    if n.startswith("崆峒山-"):      # 页面实际用「崆峒-X」，别写「崆峒山-X」\n'
           '        n = "崆峒-" + n[len("崆峒山-"):]\n')
    assert old in s
    s = s.replace(old, new, 1)
    open(S, "w", encoding="utf-8").write(s)
    print("build_wiki2: pcanon 已归一「崆峒山-X」→「崆峒-X」")
else:
    print("build_wiki2: 已有归一，跳过")

# 2) 第 5 批
p = os.path.join(BASE, "data", "place_override.json")
ov = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
BATCH = {
    # 夺魄森林：夏侯兰幽居处、夺魄门本部戏
    "S2502_01_02": ("崆峒-夺魄森林", "夏侯兰在幽居处授赵活雪山飞鸿爪，祭拜雪山"),
    "S2504_02_03": ("崆峒-夺魄森林", "夏侯兰与第三香对阵，赵活以弟子身分出头顶撞"),
    "S2504_02_06": ("崆峒-夺魄森林", "夏侯兰散功将逝，忆童年，承前场"),
    "S2510_01_01": ("崆峒-夺魄森林", "夏侯兰严训赵活，师徒在幽居处"),
    "S2600_02_03_01": ("崆峒-夺魄森林", "标题即「诱敌入夺魄森林」，飞天、玄功、铁拳弟子追入林中"),
    "ch2_5_2_3": ("崆峒-夺魄森林", "夺魄门弟子在门中游说赵活，原文「有缘入我夺魄门」"),
    "ch5_4_7_4_2": ("崆峒-夺魄森林", "夏侯兰在居处授赵活秘笈"),
    "section_01_free_02_01": ("崆峒-夺魄森林", "夏侯兰初试赵活武功，师徒日常在林中幽居"),
    "section_01_free_07_201": ("崆峒-夺魄森林", "标题即「迷路夺魄林遭擒」，旁白写冲进夺魄森林"),
    "talk_girl5_02": ("崆峒-夺魄森林", "夏侯兰说要下山捉小娘子，从林中住处下山"),
    "talk_girl5_05": ("崆峒-夺魄森林", "夏侯兰自述入崆峒被改名的往事，师徒闲谈"),
    # 镇魂狱
    "S2700_02_03_01": ("崆峒-镇魂狱", "夺魄弟子摇铃召援，原文「随我们到镇魂狱问话」"),
    "S2800_03_06": ("崆峒-镇魂狱", "标题即「夺魄牢中错保他人」，赵活被关在牢里"),
    "craft_work_505": ("崆峒-镇魂狱", "原文「到夺魄峰镇魂狱域修缮监牢」"),
    # 铁拳巷（大铁舖）
    "S2901_04_01": ("崆峒-铁拳巷", "余郁两家说亲，场景在大铁舖一带，小竹踏裂地砖躲走"),
    "S2915_01": ("崆峒-铁拳巷", "赵活想向小竹借工具，原文「今日大铁舖不开张吗」"),
    # 崆峒山（无更细证据）
    "S0014_01_03": ("崆峒山", "峨嵋弟子拿赵活试点穴，在崆峒留学期间，未见具体驻地"),
    "S0014_01_06": ("崆峒山", "夏侯兰出手护赵活，玄功弟子在场，地点仍在崆峒山"),
    "S2200_04_04": ("崆峒山", "虞小梅论焚心火印速成之害，闲谈，未写所在"),
    "S2700_02_03": ("崆峒山", "赵活追捕夺魄小偷，当街追赶，未写是哪条街"),
    "S2700_02_03_02": ("崆峒山", "赵活与瑞笙背靠背血战夺魄弟子，巷战，具体处未写"),
    "S2800_02_break_start_01": ("崆峒山", "战后瑞笙坦言私心，未写所在"),
    "ch5_6_3_2_1": ("崆峒山", "丹霞子问中台战况，军情会议，未写在哪座殿"),
}
for k, (pl, why) in BATCH.items():
    ov[k] = {"place": pl, "why": why}
# 之前写错前缀的两条，改成页面真名
for k in ("section_01_free_03_01",):
    if k in ov and ov[k]["place"].startswith("崆峒山-"):
        ov[k]["place"] = "崆峒-" + ov[k]["place"][len("崆峒山-"):]
json.dump(ov, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("覆盖表", len(ov), "条")
print(collections.Counter(v["place"] or "（不标）" for v in ov.values()).most_common())
