# -*- coding: utf-8 -*-
"""统计战斗行里：有中文名的 / 只有数字键的（BattleLevel 本地化键未解）。"""
import io, json, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(BASE + r"\data\wiki.db")
c.row_factory = sqlite3.Row
CJK = re.compile(r"[\u4e00-\u9fff]")
named = numkey = other = 0
samples = []
for r in c.execute("select sections from pages where type='场景'"):
    for s in json.loads(r[0] or "[]"):
        if s.get("h") != "接下来":
            continue
        for x in (s.get("rows") or []):
            n = x.get("note") or ""
            if not n.startswith("战斗："):
                continue
            t = n[len("战斗："):]
            if CJK.search(t):
                named += 1
            elif re.fullmatch(r"\d+", t.strip()):
                numkey += 1
                if len(samples) < 6:
                    samples.append(t)
            else:
                other += 1
                if len(samples) < 8:
                    samples.append(t)
print("有中文关卡名 %d，纯数字键 %d，其他 %d" % (named, numkey, other))
print("样例:", samples)
