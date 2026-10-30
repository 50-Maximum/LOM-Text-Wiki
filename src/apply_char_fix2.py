# -*- coding: utf-8 -*-
"""第二轮并义（有原文证据的）：余公子、翟老汉/翟长老、毛帮主、申屠师叔、野利察汉势力。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"

def load(n):
    p = os.path.join(BASE, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def save(n, d):
    json.dump(d, open(os.path.join(BASE, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

cf = load("chars_fix.json")
mg = cf.setdefault("merge", {})
add = {
    "余公子": "余自咏",      # 余公子自称「花城四少余自咏」
    "翟长老": "铁拳长老",     # 同场被称翟长老/翟老汉
    "翟老汉": "铁拳长老",     # 「我翟老汉把话撂这儿」
    "毛帮主": "毛二壮",       # 「泥教畜生道法王，就是本帮帮主毛二壮」
    "申屠师叔": "申屠道长",    # 同为青城申屠
}
mg.update(add)
save("chars_fix.json", cf)
print("并义", len(add), "条：", "、".join(add))

pf = load("person_faction.json")
pf["野利察汉"] = ["西夏", "西夏权臣，中原叶家同脉族叔"]
pf["铁拳长老"] = ["铁拳门", "铁拳门长老（翟老汉）"]
save("person_faction.json", pf)

cp = load("chars_prefix.json")
cp["野利察汉"] = "西夏"
cp["铁拳长老"] = "铁拳门"
save("chars_prefix.json", cp)
print("势力：野利察汉→西夏，铁拳长老→铁拳门")
