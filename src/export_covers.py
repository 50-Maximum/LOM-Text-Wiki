# -*- coding: utf-8 -*-
"""导出书物封面：ItemBook 的 id 与 item_book_<id> 图标同名对齐，再按名字接条目。"""
import io, os, re, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "system")
BUNDLES = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\StreamingAssets\aa\StandaloneWindows64"
OUT = os.path.join(BASE, "web", "item")
os.makedirs(OUT, exist_ok=True)

# id -> 名字
book = {}
for line in open(os.path.join(RAW, "ItemBook_zh-cn.txt"), encoding="utf-8-sig"):
    if " = " not in line:
        continue
    k, v = line.rstrip("\n").split(" = ", 1)
    m = re.search(r"/Name/(\w+)$", k)
    if m:
        book[m.group(1)] = v
print("ItemBook 名字", len(book))

# 图标
icon_of = {}
for f in sorted(os.listdir(BUNDLES)):
    if not f.startswith("picture") or "_assets_all" not in f:
        continue
    env = UnityPy.load(os.path.join(BUNDLES, f))
    for o in env.objects:
        if o.type.name != "Sprite":
            continue
        try:
            nm = o.read(check_read=False).m_Name
        except Exception:
            continue
        m = re.fullmatch(r"item_book_(\w+)", nm)
        if m:
            icon_of.setdefault(m.group(1), []).append(o)
print("item_book_* 图标", len(icon_of))

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
pages = con.execute("select slug,name from pages where type='书物'").fetchall()
byname = {}
for pid, nm in book.items():
    byname.setdefault(nm, []).append(pid)

saved, nofit = {}, []
for r in pages:
    ids = byname.get(r["name"]) or []
    ids = [i for i in ids if i in icon_of]
    if not ids:
        nofit.append(r["name"])
        continue
    pid = ids[0]
    fn = "item/book_%s.png" % pid
    p = os.path.join(BASE, "web", fn.replace("/", os.sep))
    if not os.path.exists(p):
        try:
            img = icon_of[pid][0].read().image
        except Exception:
            nofit.append(r["name"])
            continue
        img.save(p)
    saved[r["slug"]] = fn

json.dump(saved, open(os.path.join(BASE, "web", "covers.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
print("书物条目 %d，配上封面 %d，未配上 %d" % (len(pages), len(saved), len(nofit)))
print("未配上示例:", nofit[:12])
