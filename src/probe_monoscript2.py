# -*- coding: utf-8 -*-
"""在所有 assets 里找 MonoScript，看 pathID 3013/1901 对应什么类；顺带列出类名分布。"""
import io, sys, os, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
files = sorted(glob.glob(os.path.join(GAME, "*.assets")))
print("文件:", [os.path.basename(f) for f in files])
want = {3013, 1901}
found = {}
for f in files:
    try:
        env = UnityPy.load(f)
    except Exception as e:
        print(" 跳过", os.path.basename(f), e); continue
    n = 0
    for o in env.objects:
        if o.type.name != "MonoScript":
            continue
        n += 1
        try:
            d = o.read()
            name = getattr(d, "m_ClassName", "") or getattr(d, "m_Name", "")
        except Exception:
            name = "?"
        if o.path_id in want:
            found.setdefault(o.path_id, []).append((os.path.basename(f), name))
    if n:
        print("%-26s MonoScript %d" % (os.path.basename(f), n))
print("\n目标脚本:", found)
