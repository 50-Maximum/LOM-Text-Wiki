# -*- coding: utf-8 -*-
"""找 BattleLevel 名字的本地化来源：全资产搜 BattleLevel / 名称键附近的字符串。"""
import io, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
NEEDLES = [b"BattleLevel", b"LeanLocalization", b"LeanPhrase"]
hits = collections.defaultdict(list)
for root, ds, fs in os.walk(GAME):
    for f in fs:
        if not f.lower().endswith((".assets", ".resS", ".bundle")):
            continue
        p = os.path.join(root, f)
        try:
            b = open(p, "rb").read()
        except Exception:
            continue
        for n in NEEDLES:
            if n in b:
                i = b.find(n)
                hits[n.decode()].append((f, len(b), i))
for k, v in hits.items():
    print("\n==", k, "命中", len(v))
    for f, sz, i in v[:4]:
        print("   %-28s %d 字节 首个位置 %d" % (f, sz, i))
