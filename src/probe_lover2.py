# -*- coding: utf-8 -*-
"""扫全库：心上人（lover）取值映射与设置场景。"""
import os, sys, io, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"

RX = re.compile(r'SetPlayer\(\s*"lover"\s*,\s*(\d+)\s*\)')
RX_MSG = re.compile(r'DisplayMessage\(\s*"心上人已变为([^"]+)"\s*\)')

val_names = collections.defaultdict(set)
where = collections.defaultdict(list)

for fn in sorted(os.listdir(RAW)):
    if not fn.endswith(".txt"):
        continue
    lines = open(os.path.join(RAW, fn), encoding="utf-8").read().splitlines()
    for i, ln in enumerate(lines):
        m = RX.search(ln)
        if not m:
            continue
        v = int(m.group(1))
        # 往下找 3 行内的提示语
        nm = ""
        for k in range(i + 1, min(i + 4, len(lines))):
            mm = RX_MSG.search(lines[k])
            if mm:
                nm = mm.group(1)
                break
        if nm:
            val_names[v].add(nm)
        where[v].append((fn[:-4], i + 1, nm))

print("== lover 取值 → 姓名 ==")
for v in sorted(val_names):
    print(f"  {v}: {'/'.join(sorted(val_names[v]))}   设置点 {len(where[v])}")

print("\n== 各值设置场景（最多 3 个）==")
for v in sorted(where):
    spots = where[v][:3]
    print(f"  {v}: " + "、".join(f"{s}#{n}" for s, n, _ in spots))
