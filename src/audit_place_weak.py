# -*- coding: utf-8 -*-
"""排查「文中提及（弱证据）」的地点归属：找出正文里明显表示人不在该地的场景。

依据与 build_wiki2.place_of 同一套：
  脚本编号 > 场景标题 > 正文/旁白线索 > 承前场 > 动身无目的地 > 文中提及
本脚本只处理最后一档「文中提及」。
"""
import io, ast, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
SRC = open(os.path.join(BASE, "src", "build_wiki2.py"), encoding="utf-8").read()
m = re.search(r"PLACE_PREFIX_KEYS = (\(.*?\))\n", SRC, re.S)
PREFIX = ast.literal_eval(m.group(1))

INFER = json.load(open(os.path.join(BASE, "data", "scene_place_infer.json"), encoding="utf-8"))
LOGIC = json.load(open(os.path.join(BASE, "data", "place_logic.json"), encoding="utf-8"))

# pcanon 简版：去掉内部前缀
def pcanon(x):
    x = (x or "").strip()
    return x

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute(
    "select script, chapter, place, title, cjk, line_count from scenes")}

weak = []
for sc, d in scenes.items():
    p = pcanon(d.get("place") or "")
    if p:
        low = sc.lower()
        if any(low.startswith(k) for k in PREFIX):
            continue
    if (INFER.get(sc) or {}).get("place"):
        continue
    if (LOGIC.get(sc) or {}).get("place"):
        continue
    if p:
        weak.append(sc)
print("「文中提及」档场景 %d 个" % len(weak))

AWAY = re.compile(r"(下山|回山|上山|上山去|赶回|出城|进城|山下|城里|街上|市集|集市|客栈|"
                  r"客舟|船上|小舟|渡船|路上|途中|动身|启程|赶路|离开|远行|出门在外|"
                  r"赶赴|前往|来到|抵达|进城去|离了)")
rows = []
for sc in weak:
    d = scenes[sc]
    hits = []
    for r in con.execute("select seq, speaker, text from lines where script=? order by seq", (sc,)):
        t = r["text"] or ""
        mm = AWAY.search(t)
        if mm:
            hits.append((r["seq"], mm.group(1), t[:90]))
    if hits:
        rows.append({"script": sc, "title": d.get("title") or "", "place": d["place"],
                     "chapter": d.get("chapter") or "", "cjk": d.get("cjk") or 0,
                     "n": len(hits), "first": hits[0], "samples": hits[:3]})

rows.sort(key=lambda x: (-x["n"], -x["cjk"]))
print("命中「人可能不在该地」表述的场景 %d 个\n" % len(rows))

out = os.path.join(BASE, "data", "place_weak_audit.md")
with open(out, "w", encoding="utf-8") as f:
    f.write("地点弱证据排查：文中提及档里出现方位/动身表述的场景\n\n")
    f.write("共 %d 场（按命中句数降序）\n\n" % len(rows))
    for i, r in enumerate(rows, 1):
        f.write("%d. %s（现标：%s｜%s｜%d 字）\n" % (i, r["title"] or r["script"], r["place"],
                                                 r["chapter"] or "?", r["cjk"]))
        f.write("   脚本 %s｜命中 %d 句\n" % (r["script"], r["n"]))
        for seq, kw, t in r["samples"]:
            f.write("   #%d [%s] %s\n" % (seq, kw, t))
        f.write("\n")
print("清单:", out)
for r in rows[:25]:
    print("%-28s %-10s %-6s 命中%d  例：#%d [%s] %s"
          % ((r["title"] or r["script"])[:26], r["place"][:8], r["chapter"][:5],
             r["n"], r["first"][0], r["first"][1], r["first"][2][:46]))
