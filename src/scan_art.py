# -*- coding: utf-8 -*-
"""扫描全部 .assets，列出 Texture2D / Sprite / Material 名字，找出与地图相关的资源。"""
import io, os, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
OUT = r"D:\LegendOfMortal Wiki\data\art_names.json"

KW = re.compile(r"map|Map|MAP|地图|舆图|world|World|background|Background|bg|BG|"
                r"scene|Scene|city|City|land|Land|plain|mountain|Mountain|"
                r"travel|Travel|route|Route|road|Road|overview|Overview", re.I)

files = [f for f in os.listdir(ROOT) if re.search(r"\.(assets|resource)$", f)]
allnames = {}
for f in sorted(files):
    p = os.path.join(ROOT, f)
    try:
        env = UnityPy.load(p)
    except Exception as e:
        print("SKIP", f, e)
        continue
    cnt = 0
    for obj in env.objects:
        if obj.type.name not in ("Texture2D", "Sprite", "Material", "RenderTexture"):
            continue
        try:
            d = obj.read(check_read=False)
            nm = getattr(d, "m_Name", None) or getattr(d, "name", "")
        except Exception:
            nm = ""
        if not nm:
            continue
        allnames.setdefault(f, []).append([obj.type.name, nm])
        cnt += 1
    print(f, cnt)

json.dump(allnames, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

hits = []
for f, arr in allnames.items():
    for t, nm in arr:
        if KW.search(nm):
            hits.append([f, t, nm])
hits.sort(key=lambda x: (x[2], x[0]))
print("\n--- 关键词命中 %d ---" % len(hits))
for f, t, nm in hits:
    print(f, t, nm)
