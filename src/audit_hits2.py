# -*- coding: utf-8 -*-
"""命中明细：对每条 ref 记录，读它对应的参考 md，列出「到底哪几句选项对上了」。"""
import io, os, re, sys, json, sqlite3
from opencc import OpenCC

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CC = OpenCC("t2s")
B = r"D:\LegendOfMortal Wiki"
SRC = r"C:\Users\Luo\Downloads\LoM-wiki-1.7.0\LoM-wiki-1.7.0\docs\event\simple"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()
ref = json.load(open(os.path.join(B, "data", "scene_time_ref.json"), encoding="utf-8"))
cal = json.load(open(os.path.join(B, "data", "ref_wiki", "calendar.json"), encoding="utf-8"))
titles = dict(c.execute("select script,title from scenes"))

def norm(s):
    return re.sub(r"[\s，。！？、；：,.!?;:「」『』()（）<>《》\-—]", "", s or "")

cho = {}
for sc, opt in c.execute("select script,options from choices"):
    try:
        arr = json.loads(opt)
    except Exception:
        continue
    txt = " / ".join(str(o.get("text") or o.get("label") or "") for o in arr if isinstance(o, dict))
    if txt:
        cho[sc] = norm(txt)
txtall = {}
for sc, tx in c.execute("select script,text from lines"):
    txtall[sc] = txtall.get(sc, "") + " " + (tx or "")
txtall = {k: norm(v) for k, v in txtall.items()}

byname = {e["name"]: e for e in cal}
for sc, v in sorted(ref.items(), key=lambda x: x[1].get("score") or 0):
    s = v.get("score") or 0
    if s < 2 or s > 4:
        continue
    name = (v.get("name") or "").split("／")[0]
    e = byname.get(name) or {}
    fn = os.path.basename(e.get("link") or "") + ".md"
    p = os.path.join(SRC, fn)
    qs = []
    if os.path.exists(p):
        t = open(p, encoding="utf-8", errors="replace").read()
        qs = [CC.convert(q) for q in re.findall(r"「([^」]{2,24})」", t)]
        qs = [q for q in qs if len(norm(q)) >= 2]
    hit = [q for q in qs if norm(q) and norm(q) in cho.get(sc, "")]
    hitline = [q for q in qs if q not in hit and norm(q) and norm(q) in txtall.get(sc, "")]
    print("%-26s %-10s 分%-2s ｜ 选项命中 %d/%d %s"
          % (sc, name, s, len(hit), len(qs), "／".join(hit)))
    if hitline:
        print("      仅在台词里: %s" % "／".join(hitline[:4]))
    print("      场景: %s" % (titles.get(sc) or "-"))
