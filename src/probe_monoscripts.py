# -*- coding: utf-8 -*-
import io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
for f in ("resources.assets", "sharedassets2.assets"):
    env = UnityPy.load(GAME + "\\" + f)
    ms = {}
    for o in env.objects:
        if o.type.name == "MonoScript":
            try:
                d = o.read()
                ms[o.path_id] = getattr(d, "m_ClassName", None) or getattr(d, "m_Name", "?")
            except Exception:
                pass
    print("\n==", f, "MonoScript:", len(ms))
    print("   类名样例:", list(ms.values())[:12])
    cnt = collections.Counter()
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                p = o.read()
                sid = p.m_Script.path_id if hasattr(p, "m_Script") else None
            except Exception:
                sid = None
            cnt[ms.get(sid, str(sid))] += 1
    for k, v in cnt.most_common(15):
        print("   %-40s %d" % (k, v))
