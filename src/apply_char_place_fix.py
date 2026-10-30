# -*- coding: utf-8 -*-
"""按五零口述修正：地点去重并义、角色并义、势力归属纠正。

1) 地点：半雨屏合并进「崆峒-半雨屏」；福州并义到「福建」；崆峒三处明确挂崆峒山。
2) 角色并义：叶云啾→叶云裳、鞠师姐→鞠冬音、阿花→虞小梅、阎尖锐/阎掌门→无相祖师、
   赵师兄→赵活、赖某人→赖裕廷、赵活师父→夏侯兰、李云弃→野利察汉。
3) 势力：赖裕廷→峨嵋派、觉空大师→嵩山派、许胜→崆峒派、老和尚→梦境。
"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"

def load(n):
    p = os.path.join(BASE, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def save(n, d):
    json.dump(d, open(os.path.join(BASE, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 地点 ----------
pe = load("place_edits.json")
ren = pe.setdefault("rename", {})
ren["半雨屏"] = "崆峒-半雨屏"
ren["福州"] = "福建"
par = pe.setdefault("parent", {})
par["崆峒-半雨屏"] = "崆峒山"
par["崆峒-大铁铺"] = "崆峒山"
par["崆峒-无色广场"] = "崆峒山"
par["崆峒-无色广场赌坊"] = "崆峒-无色广场"
save("place_edits.json", pe)
print("地点：半雨屏→崆峒-半雨屏，福州→福建，崆峒三处挂崆峒山")

# ---------- 角色并义 ----------
cf = load("chars_fix.json")
mg = cf.setdefault("merge", {})
merges = {
    "叶云啾": "叶云裳",
    "鞠师姐": "鞠冬音",
    "阿花": "虞小梅",
    "阎尖锐": "无相祖师",
    "阎掌门": "无相祖师",
    "赵师兄": "赵活",
    "赖某人": "赖裕廷",
    "赵活师父": "夏侯兰",
    "李云弃": "野利察汉",
}
mg.update(merges)
save("chars_fix.json", cf)
print("角色并义 %d 条" % len(merges))

# ---------- 势力 ----------
pf = load("person_faction.json")
fix = {
    "赖裕廷": ["峨嵋派", "峨嵋派弟子（另有金国马贼「豺狼」的身份）"],
    "觉空大师": ["嵩山派", "嵩山派达摩院首座"],
    "许胜": ["崆峒派", "崆峒派飞天门弟子"],
    "老和尚": ["梦境", "梦境中人（点化南宫浅的老和尚）"],
}
for k, v in fix.items():
    old = pf.get(k)
    pf[k] = v
    print("   势力 %-6s %s → %s" % (k, old, v))
save("person_faction.json", pf)

# ---------- 前缀（确保优先于默认「江湖」）----------
cp = load("chars_prefix.json")
for k, v in (("赖裕廷", "峨嵋派"), ("觉空大师", "嵩山派"), ("许胜", "崆峒派"),
             ("老和尚", "梦境"), ("叶云裳", "叶家"), ("鞠冬音", "崆峒派")):
    cp[k] = v
save("chars_prefix.json", cp)
print("前缀表 %d 条" % len(cp))
