# -*- coding: utf-8 -*-
"""探查 portrait bundle 结构。"""
import os, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

D = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\StreamingAssets\aa\StandaloneWindows64"
files = sorted(glob.glob(os.path.join(D, "portrait_*.bundle")))
print("portrait bundles", len(files))
f = files[0]
print("sample", os.path.basename(f), round(os.path.getsize(f) / 1048576, 1), "MB")
env = UnityPy.load(f)
kinds = {}
for obj in env.objects:
    kinds[obj.type.name] = kinds.get(obj.type.name, 0) + 1
print("对象类型", kinds)
names = []
for obj in env.objects:
    if obj.type.name in ("Sprite", "Texture2D"):
        try:
            data = obj.read()
            names.append((obj.type.name, getattr(data, "m_Name", ""), obj.path_id))
        except Exception as e:
            names.append((obj.type.name, "ERR " + str(e)[:40], obj.path_id))
print("资源数", len(names))
for n in names[:15]:
    print("   ", n)
