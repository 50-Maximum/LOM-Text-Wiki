# -*- coding: utf-8 -*-
"""试试 UnityPy 的 TypeTree：能不能按字段名直接读出 CombatLevel 的描述。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = [f for f in os.listdir(GAME) if f.endswith(".assets")]
ok = 0
for f in FILES:
    p = os.path.join(GAME, f)
    try:
        env = UnityPy.load(p)
    except Exception:
        continue
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tree = o.read_typetree()
        except Exception:
            continue
        if not isinstance(tree, dict):
            continue
        if "_desc" in tree or "m_Name" in tree and "_enemyStat" in tree:
            print("文件", f, "path_id", o.path_id)
            print("字段:", list(tree)[:18])
            print("m_Name:", tree.get("m_Name"))
            print("_desc:", repr(tree.get("_desc"))[:120])
            ok += 1
            if ok >= 3:
                sys.exit(0)
print("命中", ok)
