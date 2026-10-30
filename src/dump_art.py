# -*- coding: utf-8 -*-
"""导出指定名字的 Texture2D / Sprite 为 PNG。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
OUT = r"D:\LegendOfMortal Wiki\data\art_dump"
os.makedirs(OUT, exist_ok=True)

WANT = set(sys.argv[1:])
if not WANT:
    WANT = {"background_map", "background_map_sample"}
TYPES = {"Texture2D", "Sprite"}

files = [f for f in os.listdir(ROOT) if f.endswith((".assets", ".resource"))]
for f in sorted(files):
    try:
        env = UnityPy.load(os.path.join(ROOT, f))
    except Exception:
        continue
    for obj in env.objects:
        if obj.type.name not in TYPES:
            continue
        try:
            d = obj.read(check_read=False)
            nm = getattr(d, "m_Name", "") or ""
        except Exception:
            continue
        base = nm.rsplit("_", 1)[0] if obj.type.name == "Sprite" and nm.rsplit("_", 1)[0] in WANT else nm
        if nm not in WANT and base not in WANT:
            continue
        try:
            data = obj.read()
            img = data.image
        except Exception as e:
            print("FAIL", f, obj.type.name, nm, e)
            continue
        if img is None:
            print("NOIMAGE", f, obj.type.name, nm)
            continue
        fn = "%s__%s__%s.png" % (obj.type.name, nm, f.replace(".", "_"))
        p = os.path.join(OUT, fn)
        img.save(p)
        print("%-42s %-10s %sx%s  %s" % (nm, obj.type.name, img.width, img.height, p))
