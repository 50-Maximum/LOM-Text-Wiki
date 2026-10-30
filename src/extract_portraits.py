# -*- coding: utf-8 -*-
"""从 portrait bundle 导出立绘 PNG 到 data/portraits/。"""
import os, sys, io, glob, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

D = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\StreamingAssets\aa\StandaloneWindows64"
OUT = r"D:\LegendOfMortal Wiki\data\portraits"
os.makedirs(OUT, exist_ok=True)

files = sorted(glob.glob(os.path.join(D, "portrait*.bundle"))) + \
        sorted(glob.glob(os.path.join(D, "portarit*.bundle")))
print("bundles", len(files), flush=True)

def key_of(fn):
    name = os.path.basename(fn)
    name = re.sub(r"^portrait_|^portarit_", "", name)
    name = re.sub(r"_assets_all_.*$", "", name)
    return name.lower()

saved, failed = 0, 0
for i, f in enumerate(files, 1):
    key = key_of(f)
    try:
        env = UnityPy.load(f)
        for obj in env.objects:
            if obj.type.name != "Texture2D":
                continue
            try:
                data = obj.read()
                img = data.image
                nm = re.sub(r"[^\w\-]+", "_", data.m_Name or "tex")
                img.save(os.path.join(OUT, f"{key}__{nm}.png"))
                saved += 1
            except Exception:
                failed += 1
    except Exception as e:
        print("ERR", os.path.basename(f), str(e)[:60])
    if i % 20 == 0:
        print(f"{i}/{len(files)} saved={saved} failed={failed}", flush=True)

print("导出完成", saved, "张，失败", failed)
print("目录文件数", len(os.listdir(OUT)))
