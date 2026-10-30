# -*- coding: utf-8 -*-
"""序章 8 行专用定位器：抽出年表行里所有「选项原文」，对 choices.options 与 lines.text
同时打分，要求 ≥2 条命中，再打印候选剧本的标题与全部选项供人工确认。"""
import io, sys, json, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
db = sqlite3.connect(B + r"\wiki.db")
c = db.cursor()

tl = json.load(open(B + r"\ref_wiki\timeline.json", encoding="utf-8"))
keep = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
known = [v["name"] for v in keep.values() if v.get("name")]
rows = [r for r in tl if r["kind"] in ("主线", "支线")
        and not [n for n in known if n in r["event"]]]

cho = list(c.execute("select script,seq,options from choices"))
txt = list(c.execute("select script,seq,text from lines"))
titles = dict(c.execute("select script,title from scenes"))

# 清洗：去掉属性变动尾巴、🎲、【】判定括号
def quotes(row):
    out = []
    for m in re.findall(r"「([^」]{2,24})」", row["event"]):
        s = m.strip()
        s = re.sub(r"^[（(].*?[）)]", "", s).strip()
        if s and s not in out:
            out.append(s)
    return out

for r in rows:
    qs = quotes(r)
    score = {}
    for q in qs:
        for sc, seq, opt in cho:
            if opt and q in opt:
                score[sc] = score.get(sc, 0) + 2          # 选项命中权重高
        for sc, seq, tx in txt:
            if q in (tx or ""):
                score[sc] = score.get(sc, 0) + 1
    top = sorted(score.items(), key=lambda x: -x[1])[:4]
    print("\n=== [%s] %s年%s月%s ｜ 指纹 %d 条：%s"
          % (r["kind"], r["year"], r["month"], r.get("xun", ""), len(qs), "／".join(qs)))
    print("    " + r["event"][:70].replace("\n", " "))
    for sc, sc_ in top:
        print("    → %-28s 分%-3d %s" % (sc, sc_, (titles.get(sc) or "")[:34]))
