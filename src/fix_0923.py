# -*- coding: utf-8 -*-
"""09:23 复核修正：命名、阶段、时间；关闭投票，改为旗标/条件/原文判定。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


arcs = load("arcs.json")
sc = arcs.setdefault("scene", {})
FIX = {
    "S9001_01": "不限时间", "S9001_03": "不限时间", "S9001_04": "不限时间",
    "S0012_01_01": "南宫寿宴",
    "S9904_01": "外姓弟子", "S9904_01_02": "外姓弟子",
    "act2_3": "比武招亲",
    "talk_brother4_option_02_03": "比武招亲",
}
sc.update(FIX)
for k in ["S0204_01"]:
    pass
save("arcs.json", arcs)
print("阶段改判：", FIX)

# S0204_01 前缀全部归比武招亲：直接查库列脚本
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
s0204 = [r["script"] for r in c.execute("select script from scenes where script like 'S0204_01%'")]
sc = arcs["scene"]
for s in s0204:
    sc[s] = "比武招亲"
save("arcs.json", arcs)
print("S0204_01 前缀 %d 场 → 比武招亲" % len(s0204))

# S9001 时间与阶段矛盾，清掉时间标注
c.execute("delete from scene_time where script like 'S9001_%'")
c.commit()
print("已清 S9001_* 的攻略时间标注")

# 事件命名修正
np = load("notes_patch.json")
RENAME = {
    ("S0014_01_01", "玄功弟子拿赵活试招"): "峨嵋弟子向赵活试手",
    ("S0014_01_01", "虞小梅为赵活解穴"): "赵活被峨嵋弟子点穴",
    ("S0014_01_01", "虞小梅为赵活解穴未果"): "点穴后赵活僵在原地",
    ("S0014_01_01", "虞小梅夜送料理给赵活"): "赵活菜园取衣遭暗算",
    ("S0014_01_02", "玄功弟子拿赵活试招"): "玄功门指点峨嵋弟子以赵活试招",
    ("S0014_01_02", "玄功前辈点穴指点赵活"): "夏侯兰指点赵活拆招",
}
for (s, old), new in RENAME.items():
    np.setdefault(s, {}).setdefault(old, {})["name"] = new
    print("%s  %s → %s" % (s, old, new))
save("notes_patch.json", np)
