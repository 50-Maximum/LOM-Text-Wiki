# -*- coding: utf-8 -*-
"""选项对不上的 10 条，改用 md 正文长句反查剧本（比选项更独特的指纹）。"""
import io, os, re, sys, json, sqlite3
from opencc import OpenCC

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CC = OpenCC("t2s")
B = r"D:\LegendOfMortal Wiki"
SRC = r"C:\Users\Luo\Downloads\LoM-wiki-1.7.0\LoM-wiki-1.7.0\docs\event\simple"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()
cal = json.load(open(os.path.join(B, "data", "ref_wiki", "calendar.json"), encoding="utf-8"))
titles = dict(c.execute("select script,title from scenes"))
byname = {e["name"]: e for e in cal}

SUSPECT = ["吕翁讨债", "叶氏行踪风波", "晁和搞鬼事件集", "回归唐门", "掌门议事",
           "猴儿酒", "四师兄会合", "小梅上门", "师妹招亲前半", "师妹招亲后半"]

lines = list(c.execute("select script,text from lines"))
def norm(s):
    return re.sub(r"[\s，。！？、；：,.!?;:「」『』()（）<>《》\-—*#>|]", "", s or "")
blob = {}
for sc, tx in lines:
    blob.setdefault(sc, []).append(norm(tx))

for nm in SUSPECT:
    e = byname.get(nm) or {}
    p = os.path.join(SRC, os.path.basename(e.get("link") or "") + ".md")
    if not os.path.exists(p):
        print("\n### %s ｜ md 缺失 %s" % (nm, p)); continue
    t = CC.convert(open(p, encoding="utf-8", errors="replace").read())
    sents = [s.strip() for s in re.split(r"[\n。！？]", t)]
    fps = []
    for s in sents:
        s = re.sub(r"^[#>*\-\s|]+", "", s)
        s = re.sub(r"「[^」]*」", "", s)
        s = norm(s)
        if len(s) >= 12:
            fps.append(s)
    fps = list(dict.fromkeys(fps))[:40]
    score = {}
    for sc, parts in blob.items():
        j = "".join(parts)
        n = sum(1 for f in fps if f[:24] in j or f in j)
        if n:
            score[sc] = n
    top = sorted(score.items(), key=lambda x: -x[1])[:3]
    print("\n### %-12s ｜ 指纹 %d 条 ｜ %s%s%s" % (nm, len(fps), e.get("year"), e.get("month"), e.get("xun")))
    for sc, n in top:
        print("    %-28s 分%-3d %s" % (sc, n, (titles.get(sc) or "")[:32]))
    if not top:
        print("    无命中")
