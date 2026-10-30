# -*- coding: utf-8 -*-
"""看 catalog 里的资源地址结构 + 本地化表里的物品/角色键名。"""
import io, os, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\StreamingAssets\aa"
cat = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
ids = cat["m_InternalIds"]
print("InternalIds", len(ids))
hits = [x for x in ids if re.search(r"portrait|Portrait|picture|item", x, re.I)]
print("portrait/picture/item 命中", len(hits))
for x in hits[:25]:
    print("   ", x)

print("\n--- InternalIds 里的非 bundle 条目 ---")
nb = [x for x in ids if not x.endswith(".bundle")]
print(len(nb))
for x in nb[:25]:
    print("   ", x)

# 本地化表
RAW = r"D:\LegendOfMortal Wiki\data\raw\system"
for f in ("ItemMisc_zh-cn.txt", "ItemBook_zh-cn.txt", "Character_zh-cn.txt", "Talent_zh-cn.txt"):
    p = os.path.join(RAW, f)
    if not os.path.exists(p):
        print("缺", f)
        continue
    s = open(p, encoding="utf-8-sig").read()
    print("\n===== %s  (%d 字) =====" % (f, len(s)))
    print("\n".join(s.splitlines()[:12]))
