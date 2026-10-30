# -*- coding: utf-8 -*-
"""全游戏目录搜 "EnemyTeam" 字面量，定位本地化数据实际存放位置。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"E:\Game\steamapps\common\LegendOfMortal"
NEEDLE = b"EnemyTeam"
hits = []
for dirpath, dirs, files in os.walk(ROOT):
    for fn in files:
        p = os.path.join(dirpath, fn)
        try:
            if os.path.getsize(p) > 200 * 1024 * 1024:
                continue
            b = open(p, "rb").read()
        except Exception:
            continue
        i = b.find(NEEDLE)
        if i >= 0:
            hits.append((os.path.relpath(p, ROOT), len(b), i, b.count(NEEDLE)))
print("命中文件", len(hits))
for h in hits[:20]:
    print("   %-56s %8d 字节  位置 %-9d 出现 %d 次" % h)
