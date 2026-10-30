# -*- coding: utf-8 -*-
"""导出待命名地图事件（无原生名且剧本标题不可用）的全文，供人工命名。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
pe = json.load(open(os.path.join(BASE, "data", "position_events.json"), encoding="utf-8"))
by_name = {}
for x in pe:
    by_name.setdefault(x["name"], x)

rows = []
for r in c.execute("select name,slug,infobox from pages where type='地图事件' and slug!='地图事件/索引'"):
    inf = json.loads(r["infobox"] or "{}")
    if (inf.get("名称来源") or "") != "地点＋结果":
        continue
    code = inf.get("事件编号")
    src = by_name.get(code) or {}
    sc = pm.get(code)
    lines = []
    if sc:
        lines = [x["text"] for x in c.execute(
            "select text from lines where script=? order by seq", (sc,))]
    txt = "".join(lines).replace("\n", "")
    rows.append({"code": code, "cur": r["name"], "key": src.get("key"),
                 "rate": src.get("rate"), "cond": src.get("cond"),
                 "script": sc, "text": txt})

rows.sort(key=lambda x: (x["code"] or ""))
out = os.path.join(BASE, "data", "_map_evt_todo.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("导出", len(rows), "→", out)

with open(os.path.join(BASE, "data", "_map_evt_todo.txt"), "w", encoding="utf-8") as f:
    for x in rows:
        f.write("%s\t%s\t%s\n" % (x["code"], x["key"], x["text"][:160]))
print("文本清单已写")
