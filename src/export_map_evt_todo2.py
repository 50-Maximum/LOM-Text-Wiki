# -*- coding: utf-8 -*-
"""导出待命名地图事件 v2：Section 类走 family 映射解析出剧本，再取全文。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
DB = os.path.join(BASE, "data", "wiki.db")
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
fam = json.load(open(os.path.join(BASE, "data", "position_script_family.json"), encoding="utf-8"))
pe = json.load(open(os.path.join(BASE, "data", "position_events.json"), encoding="utf-8"))
by_name = {}
for x in pe:
    by_name.setdefault(x["name"], x)

def resolve(code, value):
    sc = pm.get(code)
    if sc:
        return sc
    lst = fam.get(code)
    if not lst:
        return None
    if isinstance(lst, str):
        lst = [lst]
    v = (value or "").strip()
    for s in lst:
        if v and str(s).endswith(v):
            return s
    return lst[0] if lst else None

rows = []
seen = set()
for r in c.execute("select name,slug,infobox from pages where type='地图事件' and slug!='地图事件/索引'"):
    inf = json.loads(r["infobox"] or "{}")
    if (inf.get("名称来源") or "") != "地点＋结果":
        continue
    code = inf.get("事件编号")
    src = by_name.get(code) or {}
    sc = resolve(code, src.get("value"))
    lines = []
    if sc:
        lines = [x["text"] for x in c.execute(
            "select text from lines where script=? order by seq", (sc,))]
    txt = "".join(lines).replace("\n", "")
    rows.append({"code": code, "slug": r["slug"], "cur": r["name"], "key": src.get("key"),
                 "value": src.get("value"), "script": sc, "n": len(lines), "text": txt})
    seen.add(code)

rows.sort(key=lambda x: (x["code"] or ""))
json.dump(rows, open(os.path.join(BASE, "data", "_map_evt_todo.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(BASE, "data", "_map_evt_todo.txt"), "w", encoding="utf-8") as f:
    for x in rows:
        f.write("%s\t%s\t%s\t%s\n" % (x["code"], x["key"], x["script"] or "-", x["text"][:150]))
print("导出", len(rows))
print("有正文", sum(1 for x in rows if x["text"]), "无正文", sum(1 for x in rows if not x["text"]))
for x in rows[:4]:
    print("  ", x["code"], x["script"], x["n"], x["text"][:40])
