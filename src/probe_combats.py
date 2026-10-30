# -*- coding: utf-8 -*-
"""看判定库 Combats / CombatDeaths 能否给出战斗名，用于「接下来」里的战斗行。"""
import io, gzip, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"
lib = json.load(open(P, encoding="utf-8"))
print("顶层键:", list(lib)[:10])
for k in ("Combats", "CombatDeaths"):
    v = lib.get(k)
    if isinstance(v, dict):
        print("\n%s 条数 %d" % (k, len(v)))
        for i, (a, b) in enumerate(v.items()):
            print("   ", a, "→", str(b)[:120])
            if i >= 4:
                break
    elif isinstance(v, list):
        print("\n%s 条数 %d，样例 %s" % (k, len(v), str(v[:2])[:200]))
    else:
        print("\n%s:" % k, str(v)[:120])
