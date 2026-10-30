# -*- coding: utf-8 -*-
"""第四轮：按原文明确表述补势力，火护法并入颜疆。只收有原句支撑的。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"

def load(n):
    p = os.path.join(BASE, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def save(n, d):
    json.dump(d, open(os.path.join(BASE, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 并义（有原句：「我崆峒火护法颜疆颜大侠」）
cf = load("chars_fix.json"); mg = cf.setdefault("merge", {})
mg["火护法"] = "颜疆"
mg["点苍剑圣"] = "剑圣"
save("chars_fix.json", cf)

# 势力（原句见 report）
FIX = {
    "白猿祖师": ["峨嵋派", "峨嵋派开山祖师，传猿公剑、通臂拳、猿王棍"],
    "象池修士": ["峨嵋派", "峨嵋象池修士，曾与点苍剑圣、七星剑主乐山论剑"],
    "翼王": ["金国", "金国翼王完颜珣，后即位为金国皇帝"],
    "剑圣": ["点苍派", "点苍剑圣，与七星剑主并称"],
    "点苍双尊": ["点苍派", ""],
    "七星剑主": ["岭南派", "岭南剑派祖师，七星剑一脉"],
    "岭南七星剑主": ["岭南派", ""],
    "泥教法王": ["泥教", ""],
    "全真道兄": ["全真派", ""],
    "金乌": ["崆峒派", "崆峒新任掌派人，号金乌上人"],
}
pf = load("person_faction.json")
cp = load("chars_prefix.json")
for k, v in FIX.items():
    pf[k] = v
    cp[k] = v[0]
save("person_faction.json", pf)
save("chars_prefix.json", cp)
print("势力修正 %d 条、并义 2 条" % len(FIX))
for k, v in FIX.items():
    print("   %-8s → %s" % (k, v[0]))
