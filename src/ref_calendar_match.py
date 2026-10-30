# -*- coding: utf-8 -*-
"""用参考 wiki 简易事件的选项文案，反查对应剧本，从而给出年/月/旬。
做法：参考 md 里引号选项 → 在本地 choices.options 里找同一句 → 命中最多者的 script。
"""
import io, os, re, sys, json, sqlite3
from opencc import OpenCC

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CC = OpenCC("t2s")
BASE = r"D:\LegendOfMortal Wiki"
SRC = r"C:\Users\Luo\Downloads\LoM-wiki-1.7.0\LoM-wiki-1.7.0\docs\event\simple"
cal = json.load(open(os.path.join(BASE, "data", "ref_wiki", "calendar.json"), encoding="utf-8"))

c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db")).cursor()
rows = c.execute("select script,options from choices").fetchall()
print("本地判定选项组 %d 条" % len(rows))
idx = []
for sc, opt in rows:
    try:
        arr = json.loads(opt)
    except Exception:
        continue
    txt = " / ".join(str(o.get("text") or o.get("label") or "") for o in arr if isinstance(o, dict))
    if txt:
        idx.append((sc, txt))

def norm(s):
    return re.sub(r"[\s，。！？、；：,.!?;:「」『』()（）<>《》\-—]", "", s)

out = {}
hit_names = 0
for e in cal:
    link = e.get("link") or ""
    fn = os.path.basename(link) + ".md"
    p = os.path.join(SRC, fn)
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8", errors="replace").read()
    quotes = [CC.convert(q) for q in re.findall(r"「([^」]{2,24})」", t)]
    quotes = [q for q in quotes if len(norm(q)) >= 2]
    if not quotes:
        continue
    best, bestn = "", 0
    for sc, txt in idx:
        ntxt = norm(txt)
        hit = sum(1 for q in quotes if norm(q) and norm(q) in ntxt)
        if hit > bestn:
            best, bestn = sc, hit
    if best and bestn >= 1:
        hit_names += 1
        # 同一剧本保留最早一次（按年/月/旬排序靠前者）
        if best not in out:
            out[best] = {"year": e["year"], "month": e["month"], "xun": e["xun"],
                         "name": e["name"], "score": bestn}
json.dump(out, open(os.path.join(BASE, "data", "scene_time_ref.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("年表 %d 条，能反查到剧本 %d 条" % (len(cal), len(out)))
for sc, v in list(out.items())[:8]:
    print("   %-24s %s%s%s  %s（口径命中 %d）" % (sc, v["year"], v["month"], v["xun"],
                                                  v["name"], v["score"]))
