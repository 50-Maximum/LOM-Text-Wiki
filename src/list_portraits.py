# -*- coding: utf-8 -*-
"""列出所有 portrait bundle 里的贴图名。"""
import os, sys, io, glob, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

D = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\StreamingAssets\aa\StandaloneWindows64"
files = sorted(glob.glob(os.path.join(D, "portrait*.bundle"))) + \
        sorted(glob.glob(os.path.join(D, "portarit*.bundle")))
print("bundles", len(files))
out = []
for i, f in enumerate(files, 1):
    try:
        env = UnityPy.load(f)
        for obj in env.objects:
            if obj.type.name == "Texture2D":
                try:
                    out.append((os.path.basename(f), obj.read().m_Name))
                except Exception:
                    pass
    except Exception as e:
        print("ERR", os.path.basename(f), str(e)[:60])
    if i % 20 == 0:
        print(i, "/", len(files), flush=True)
json.dump(out, open(r"D:\LegendOfMortal Wiki\data\portrait_names.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
print("贴图总数", len(out))
print("样例：")
for x in out[:20]:
    print("   ", x[1])
