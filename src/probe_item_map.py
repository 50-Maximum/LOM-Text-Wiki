# -*- coding: utf-8 -*-
"""弄清 item_<类>_<号> 与本地化表（Misc/Special/Book/Equipment）的对应关系。"""
import io, os, re, sys, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "system")
BUNDLES = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\StreamingAssets\aa\StandaloneWindows64"

TABLES = {"misc": "ItemMisc_zh-cn.txt", "special": "ItemSpecial_zh-cn.txt",
          "book": "ItemBook_zh-cn.txt", "equip": "Equipment_zh-cn.txt",
          "upgrade": "UpgradeItem_zh-cn.txt"}
names = {}
for tag, fn in TABLES.items():
    p = os.path.join(RAW, fn)
    d = {}
    for line in open(p, encoding="utf-8-sig"):
        if " = " not in line:
            continue
        k, v = line.rstrip("\n").split(" = ", 1)
        m = re.search(r"/Name/(\w+)$", k)
        if m:
            d[m.group(1)] = v
    names[tag] = d
    print("%-8s 名字 %d 条，示例 %s" % (tag, len(d), list(d.items())[:3]))

icons = []
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
        if nm.startswith("item_"):
            icons.append((nm, f))
print("\nitem_* 图标 %d 个 / 文件 %s" % (len(icons),
      sorted({f for _, f in icons})))

cats = collections.Counter(re.match(r"item_([a-z_]+?)_\d+$", nm).group(1)
                           for nm, _ in icons if re.match(r"item_([a-z_]+?)_\d+$", nm))
print("类别:", dict(cats))

for tag, d in names.items():
    hit = 0
    for nm, _ in icons:
        m = re.match(r"item_([a-z_]+?)_(\d+)$", nm)
        if not m:
            continue
        num = m.group(2)
        for key in (num, num.lstrip("0"), num.zfill(4), num.zfill(5)):
            if key in d:
                hit += 1
                break
    print("   与 %-8s 号匹配 %d" % (tag, hit))

print("\n示例：")
shown = 0
for nm, _ in icons:
    m = re.match(r"item_([a-z_]+?)_(\d+)$", nm)
    if not m:
        continue
    num, cat = m.group(2), m.group(1)
    cand = {}
    for tag, d in names.items():
        for key in (num, num.lstrip("0"), num.zfill(4)):
            if key in d:
                cand[tag] = d[key]
                break
    if cand and shown < 20:
        print("   %-22s %s" % (nm, cand))
        shown += 1
