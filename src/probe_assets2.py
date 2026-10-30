# -*- coding: utf-8 -*-
import io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
env = UnityPy.load(GAME + "\\sharedassets2.assets")
# GameObject 名字
names = []
for o in env.objects:
    if o.type.name == "GameObject":
        try:
            d = o.read()
            names.append(d.m_Name)
        except Exception:
            pass
kw = [n for n in names if any(k in str(n).lower() for k in ("event", "schedule", "quest", "dialog", "story", "flag", "cond"))]
print("GameObject 名数:", len(names), " 关键词命中:", len(kw))
print(kw[:40])
print("\n随机名字样例:", names[:20])

# MonoBehaviour 前几个
mb = [o for o in env.objects if o.type.name == "MonoBehaviour"]
print("\nMonoBehaviour:", len(mb))
for o in mb[:5]:
    try:
        d = o.read()
        attrs = [a for a in dir(d) if not a.startswith("_")][:14]
        print("  ", type(d).__name__, attrs)
    except Exception as e:
        print("  读失败", type(e).__name__, str(e)[:80])
