# -*- coding: utf-8 -*-
"""第三轮：五零点名修正 + 按明确句式自动纠「江湖」前缀。

点名：
  王公子=王二壮、辣手相公=唐铮、裴红腊→青城派、胡壹千=胡离火→崆峒派、
  百万赵活→梦境（梦境小竹造的机关人，鹦鹉事件后由梦中鹦鹉驾驶）
自动：句子里出现「我乃/我是/在下/本门/敝门…」+ 势力词 + 人名，或
      势力标记说话人称呼其为师侄/师兄弟/师兄/师弟 → 判为该势力。
"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(BASE, "wiki.db"))
c.row_factory = sqlite3.Row

def load(n):
    p = os.path.join(BASE, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def save(n, d):
    json.dump(d, open(os.path.join(BASE, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 点名 ----------
cf = load("chars_fix.json"); mg = cf.setdefault("merge", {})
named = {"王公子": "王二壮", "辣手相公": "唐铮", "胡壹千": "胡离火"}
mg.update(named)
save("chars_fix.json", cf)

pf = load("person_faction.json")
pf["裴红腊"] = ["青城派", "青城派弟子（青城长老称其师侄）"]
pf["胡离火"] = ["崆峒派", "崆峒派飞天门火龙仙君座下弟子，号火狐狸"]
pf["百万赵活"] = ["梦境", "梦境小竹打造的机关人；触发鹦鹉事件后由梦中鹦鹉驾驶"]
pf["王二壮"] = pf.get("王二壮") or ["丐帮", "丐帮帮主"]
save("person_faction.json", pf)

cp = load("chars_prefix.json")
cp.update({"裴红腊": "青城派", "胡离火": "崆峒派", "百万赵活": "梦境"})
save("chars_prefix.json", cp)

intro = load("intros_char.json")
intro["百万赵活"] = ("梦境小竹打造的机关人。触发鹦鹉事件之后，梦里的鹦鹉会驾驶这具机关人出战，"
                     "郁竹在梦中喊「出击，百万赵活」。")
save("intros_char.json", intro)
print("点名修正：王公子→王二壮、辣手相公→唐铮、胡壹千→胡离火；裴红腊/胡离火/百万赵活 势力已改")

# ---------- 自动纠前缀 ----------
FAC = [("飞天", "崆峒派"), ("玄功", "崆峒派"), ("崆峒", "崆峒派"), ("青城", "青城派"),
       ("峨嵋", "峨嵋派"), ("峨眉", "峨嵋派"), ("唐门", "唐门"), ("丐帮", "丐帮"),
       ("锦香", "锦香宫"), ("点苍", "点苍派"), ("铁拳", "铁拳门"), ("嵩山", "嵩山派"),
       ("雪山", "雪山派"), ("岭南", "岭南派"), ("南宫", "南宫世家"), ("少林", "少林"),
       ("全真", "全真派"), ("飞石", "飞石帮")]
SELF = re.compile(r"我(?:乃|是|等|们|家)|在下|敝门|本门|本派|师门")
KIN = re.compile(r"师侄|师兄弟|师兄|师弟|师姐|师妹|师叔|师伯")

rows = list(c.execute("select name from pages where type='人物' and name like '江湖·%'"))
print("\n江湖前缀人物 %d 个，开始按句式取证" % len(rows))
fixed, unsure = [], []
for r in rows:
    base = r["name"].split("·")[-1]
    if len(base) < 2:
        continue
    votes = collections.Counter()
    for x in c.execute("select speaker,text from lines where text like ? limit 300", ("%" + base + "%",)):
        t, sp = x["text"] or "", x["speaker"] or ""
        facs = [f for k, f in FAC if k in t]
        if not facs:
            continue
        if SELF.search(t) and base in t:
            votes[facs[0]] += 2
        elif KIN.search(t) and any(k in sp for k, _ in FAC):
            for k, f in FAC:
                if k in sp:
                    votes[f] += 1
    if not votes:
        continue
    fac, n = votes.most_common(1)[0]
    tot = sum(votes.values())
    if n >= 3 and n / tot >= 0.75:
        fixed.append((base, fac, n, tot))
        pf[base] = [fac, (pf.get(base) or ["", ""])[1] if isinstance(pf.get(base), list) and len(pf.get(base)) > 1 else ""]
        cp[base] = fac
    else:
        unsure.append((base, fac, n, tot))

save("person_faction.json", pf)
save("chars_prefix.json", cp)
print("自动修正 %d 个：" % len(fixed))
for f in fixed:
    print("   %-10s → %-8s %d/%d" % f)
print("存疑 %d 个（未改）：" % len(unsure))
for f in unsure[:12]:
    print("   %-10s 倾向 %-8s %d/%d" % f)
