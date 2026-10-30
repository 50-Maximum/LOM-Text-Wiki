# -*- coding: utf-8 -*-
"""扫场景文件（level0..level10，无扩展名）里的 GameObject/UI 名字，找大地图节点。"""
import io, os, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
KW = re.compile(r"map|Map|地图|world|World|pos_|Pos_|Position", re.I)

files = [f for f in os.listdir(ROOT) if re.fullmatch(r"level\d+", f)]
print("场景文件:", files)
for f in sorted(files):
    try:
        env = UnityPy.load(os.path.join(ROOT, f))
    except Exception as e:
        print("SKIP", f, e)
        continue
    names = []
    for obj in env.objects:
        if obj.type.name != "GameObject":
            continue
        try:
            nm = obj.read(check_read=False).m_Name
        except Exception:
            continue
        if nm:
            names.append(nm)
    hit = [n for n in names if KW.search(n)]
    print("\n%s  GameObject=%d 命中=%d" % (f, len(names), len(hit)))
    for n in hit[:40]:
        print("   ", n)
