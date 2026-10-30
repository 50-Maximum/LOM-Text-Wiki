# -*- coding: utf-8 -*-
import io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
try:
    import UnityPy
except Exception as e:
    print("无 UnityPy:", e); raise SystemExit
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
for f in ("resources.assets", "sharedassets0.assets", "sharedassets2.assets"):
    try:
        env = UnityPy.load(GAME + "\\" + f)
    except Exception as e:
        print(f, "打开失败", e); continue
    cnt = collections.Counter()
    for o in env.objects:
        cnt[o.type.name] += 1
    print("\n==", f, "对象", sum(cnt.values()))
    for k, v in cnt.most_common(9):
        print("   ", k, v)
