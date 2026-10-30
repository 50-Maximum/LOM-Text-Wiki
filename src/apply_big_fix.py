# -*- coding: utf-8 -*-
"""大批量修正：改名、并义、势力、绰号、地点改判。

先打印龙湘相关引号短语，便于确认三个绰号是否在正文里。
"""
import io, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(BASE, "wiki.db"))
c.row_factory = sqlite3.Row

def load(n):
    p = os.path.join(BASE, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def save(n, d):
    json.dump(d, open(os.path.join(BASE, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 0) 龙湘 引号短语（只打印，不写） ----------
print("== 龙湘 相关引号短语 ==")
seen = set()
for r in c.execute("select script,seq,text from lines where text like '%龙湘%' limit 400"):
    for m in re.finditer(r"[「『“]([^」』”]{2,10})[」』”]", r["text"] or ""):
        s = m.group(1)
        if s not in seen and ("仙" in s or "侠" in s or "姬" in s or "娘" in s or "魔" in s):
            seen.add(s)
            print("   %-10s [%s#%d]" % (s, r["script"], r["seq"]))
print("   共", len(seen))

# ---------- 1) 地点改判：ch3_1_6_4 → 青城山 ----------
po = load("place_override.json")
po["ch3_1_6_4"] = "青城山"
save("place_override.json", po)
print("\n地点：ch3_1_6_4 → 青城山")

# ---------- 2) 角色并义 / 删除 ----------
cf = load("chars_fix.json")
mg = cf.setdefault("merge", {})
mg.update({
    "七星剑主": "南溪",
    "岭南七星剑主": "南溪",
    "苏迎香": "温夫人",
})
dl = cf.setdefault("delete", [])
for x in ("点苍双尊",):
    if x not in dl:
        dl.append(x)
save("chars_fix.json", cf)
print("并义：七星剑主/岭南七星剑主→南溪，苏迎香→温夫人；删除 点苍双尊")

# ---------- 3) 势力 ----------
pf = load("person_faction.json")
cp = load("chars_prefix.json")
FAC = {
    "谭霸刀": ["江湖", "无门无派的江湖恶客"],
    "牛长寿": ["江湖", "无门无派"],
    "吕员外": ["市井", "地方富户"],
    "朱婶": ["市井", "市井妇人"],
    "孟仙谣": ["朝廷", "朝廷中人，枣阳孟县主"],
    "南溪": ["岭南派", "岭南剑派七星剑主一脉传人"],
    "温夫人": ["锦香宫", "锦香宫宫主"],
    "观云客": ["点苍派", "点苍双尊之一，观云听海双尊"],
    "听海生": ["点苍派", "点苍双尊之一，观云客师弟"],
    "司徒玄空": ["峨嵋派", "峨嵋开山祖师，号白猿祖师"],
    "完颜珣": ["金国", "金国皇帝，封翼王"],
}
for k, v in FAC.items():
    pf[k] = v
    cp[k] = v[0]
save("person_faction.json", pf)
save("chars_prefix.json", cp)
print("势力修正 %d 条" % len(FAC))

# ---------- 4) 改名（走并义） ----------
mg = cf.setdefault("merge", {})
mg.update({
    "白猿祖师": "司徒玄空",
    "翼王": "完颜珣",
    "金乌": "金乌上人",
    "福韫禅师": "福韫",
})
save("chars_fix.json", cf)
print("改名并义：白猿祖师→司徒玄空、翼王→完颜珣、金乌→金乌上人、福韫禅师→福韫")

# ---------- 5) 绰号 ----------
ct = load("chars_title.json")
NICK = {
    "唐铮": "辣手相公",
    "唐升": "儒侠",
    "温夫人": "人间道法王",
    "颜疆": "山火",
    "上官隼": "上官家主",
    "段智秀": "清烟剑客",
    "宋悲": "御前带刀侍卫",
    "申屠龙": "千灯楼主",
    "解无尘": "风神",
    "丹霞子": "道法将军",
    "司徒玄空": "白猿祖师",
    "完颜珣": "金国皇帝",
    "南溪": "七星剑主",
    "叶云舟": "苍松剑客",
}
ct.update(NICK)
save("chars_title.json", ct)
print("绰号写入 %d 条" % len(NICK))
