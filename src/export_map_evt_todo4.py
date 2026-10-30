# -*- coding: utf-8 -*-
"""地图事件剧本解析 v4：Section_XX_YY_ZZ_* → section_XX_free_YY_ZZ_<value>。
导出全部待命名事件正文（从 lines 表取，取不到再退回 raw 里的中文字符串）。"""
import io, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW_S = os.path.join(BASE, "data", "raw", "scripts")
DB = os.path.join(BASE, "data", "wiki.db")
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
fam = json.load(open(os.path.join(BASE, "data", "position_script_family.json"), encoding="utf-8"))
pe = json.load(open(os.path.join(BASE, "data", "position_events.json"), encoding="utf-8"))
by_name = {}
for x in pe:
    by_name.setdefault(x["name"], x)

files = {fn[:-4] for fn in os.listdir(RAW_S) if fn.endswith(".txt")}

def section_base(code):
    m = re.match(r"Section_(\d+)_(\d+)_(\d+)_", code)
    if m:
        return "section_%s_free_%s_%s" % m.groups()
    m = re.match(r"Section_(\d+)_(\d+)_Start_", code)
    if m:
        return "section_%s_free_%s_start" % (m.group(1), m.group(2))
    return None

def resolve(code, value):
    v = (value or "").strip()
    bases = []
    sc = pm.get(code)
    if sc:
        bases.append(sc)
    sb = section_base(code)
    if sb:
        bases.append(sb)
    fl = fam.get(code) or []
    if isinstance(fl, str):
        fl = [fl]
    bases += [b for b in fl if b not in bases]
    for b in bases:
        if v:
            for cand in (b + "_" + v, b + "_" + v + "_01"):
                if cand in files:
                    return cand
            hits = sorted(k for k in files if k.startswith(b + "_" + v))
            if hits:
                return hits[0]
    for b in bases:
        if b in files:
            return b
    return None

def text_of(sc):
    if not sc:
        return ""
    ls = [x[0] for x in c.execute("select text from lines where script=? order by seq", (sc,))]
    if ls:
        return "".join(ls).replace("\n", " ")
    p = os.path.join(RAW_S, sc + ".txt")
    if not os.path.exists(p):
        return ""
    raw = open(p, encoding="utf-8", errors="ignore").read()
    cand = re.findall(r'"([^"]{4,})"', raw)
    cand = [x for x in cand if re.search(r"[\u4e00-\u9fff]", x)
            and not re.search(r"[\\/]|\.png|\.jpg|^[a-z_0-9]+$", x)]
    return "".join(cand)

rows = []
for r in c.execute("select name,slug,infobox from pages where type='地图事件' and slug!='地图事件/索引'"):
    inf = json.loads(r["infobox"] or "{}")
    if (inf.get("名称来源") or "") != "地点＋结果":
        continue
    code = inf.get("事件编号")
    src = by_name.get(code) or {}
    sc = resolve(code, src.get("value"))
    rows.append({"code": code, "slug": r["slug"], "cur": r["name"], "key": src.get("key"),
                 "value": src.get("value"), "script": sc, "text": text_of(sc)[:260]})

rows.sort(key=lambda x: (x["code"] or ""))
json.dump(rows, open(os.path.join(BASE, "data", "_map_evt_todo.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(BASE, "data", "_map_evt_todo.txt"), "w", encoding="utf-8") as f:
    for x in rows:
        f.write("%s\t%s\t%s\n" % (x["code"], x["key"], x["text"]))
print("导出", len(rows), "空文本", sum(1 for x in rows if not x["text"]))
