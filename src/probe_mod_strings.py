# -*- coding: utf-8 -*-
import io, sys, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\LOMAssistant.dll"
raw = open(p, "rb").read()
print("大小", len(raw))
asc = re.findall(rb"[\x20-\x7e]{4,}", raw)
names = [s.decode("ascii", "ignore") for s in asc]
kw = collections.Counter()
for n in names:
    for k in ("Event", "Condition", "Cond", "Trigger", "Free", "Require", "Unlock", "Hint", "Dump", "Export"):
        if k in n:
            kw[k] += 1
print("关键词计数:", kw)
picks = [n for n in names if re.search(r"(Event|Trigger|Require|Unlock|Dump)", n)]
print("相关标识符 %d 个，样例:" % len(picks))
seen = set()
for n in picks:
    if n in seen:
        continue
    seen.add(n)
    print("   ", n[:110])
    if len(seen) >= 60:
        break
