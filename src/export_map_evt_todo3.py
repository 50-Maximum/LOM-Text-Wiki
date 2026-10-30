# -*- coding: utf-8 -*-
"""导出待命名地图事件 v3：Section 类按 family 基名 + value 拼出真实剧本（section_01_free_01_301）。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW_S = os.path.join(BASE, "data", "raw", "scripts")
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
fam = json.load(open(os.path.join(BASE, "data", "position_script_family.json"), encoding="utf-8"))
pe = json.load(open(os.path.join(BASE, "data", "position_events.json"), encoding="utf-8"))
by_name = {}
for x in pe:
    by_name.setdefault(x["name"], x)

def exists(sc):
    return os.path.exists(os.path.join(RAW_S, sc + ".txt"))

def resolve(code, value):
    v = (value or "").strip()
    sc = pm.get(code)
    bases = fam.get(code) or []
    if isinstance(bases, str):
        bases = [bases]
    if sc and sc not in bases:
        bases = [sc] + list(bases)
    # 先试「基名_value」，再退回基名
    for b in bases:
        if v and exists(b + "_" + v):
            return b + "_" + v
    for b in bases:
        if exists(b):
            return b
    return sc or (bases[0] if bases else None)

rows = []
for r in c.execute("select name,slug,infobox from pages where type='地图事件' and slug!='地图事件/索引'"):
    inf = json.loads(r["infobox"] or "{}")
    if (inf.get("名称来源") or "") != "地点＋结果":
        continue
    code = inf.get("事件编号")
    src = by_name.get(code) or {}
    sc = resolve(code, src.get("value"))
    txt = ""
    if sc:
        _ls = [x[0] for x in c.execute("select text from lines where script=? order by seq", (sc,))]
        if _ls:
            txt = "".join(_ls).replace("\n", " ")
    if not txt and sc and exists(sc):
        import re as _re
        raw = open(os.path.join(RAW_S, sc + ".txt"), encoding="utf-8", errors="ignore").read()
        cand = _re.findall(r'"([^"]{4,})"', raw)
        cand = [x for x in cand if _re.search(r"[\u4e00-\u9fff]", x)
                and not _re.search(r"[\\/]|\.png|\.jpg|^[a-z_0-9]+$", x)]
        txt = "".join(cand)
    txt = txt[:300]
    rows.append({"code": code, "slug": r["slug"], "cur": r["name"], "key": src.get("key"),
                 "value": src.get("value"), "script": sc, "text": txt})

rows.sort(key=lambda x: (x["code"] or ""))
json.dump(rows, open(os.path.join(BASE, "data", "_map_evt_todo.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(BASE, "data", "_map_evt_todo.txt"), "w", encoding="utf-8") as f:
    for x in rows:
        f.write("%s\t%s\t%s\n" % (x["code"], x["key"], x["text"][:200]))
print("导出", len(rows), "有空文本", sum(1 for x in rows if not x["text"]))
for x in rows:
    if x["code"].startswith("Section_01_01"):
        print("  ", x["code"], x["script"], x["text"][:60])
