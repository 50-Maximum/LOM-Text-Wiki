# -*- coding: utf-8 -*-
"""五零 2026-10-28 指名的修正：王二壮/雷谦/火龙仙君/吕翁 + 前缀对齐。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 1) 绰号 / 称号
ct = load("chars_title.json")
for who, ti in [("王二壮", "畜生道法王"), ("雷谦", "铁拳掌门"), ("火龙仙君", "飞天掌门")]:
    old = ct.get(who, "")
    ct[who] = ti
    print("称号 %-8s %-8s → %s" % (who, old or "-", ti))
save("chars_title.json", ct)

# 2) 毛二壮 并入 王二壮（同为本帮帮主兼泥教畜生道法王）
cf = load("chars_fix.json")
mg = cf.setdefault("merge", {})
mg["毛二壮"] = "王二壮"
print("并义 毛二壮 → 王二壮")
save("chars_fix.json", cf)

# 3) 前缀
cp = load("chars_prefix.json")
for who, fc in [("吕翁", "市井")]:
    old = cp.get(who, "")
    cp[who] = fc
    print("归属 %-8s %-10s → %s" % (who, old or "-", fc))
save("chars_prefix.json", cp)

# 4) 额外势力：华山派
ef = load("extra_factions.json")
ef["华山派"] = {
    "parent": "全真派",
    "text": "华山一支源出陈抟老祖，称老华山派，「神算子」周浊即系出此派。"
            "全真七子之一郝大通精通老庄易经，算到华山有奇遇，得希夷祖师《睡功》后有所感悟，"
            "另开全真华山派。养明道人裘志攘是华山派第二代弟子，孟珙年少习武时曾受他提点。",
}
save("extra_factions.json", ef)
print("额外势力 华山派 已写入")
