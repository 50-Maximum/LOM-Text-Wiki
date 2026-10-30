# -*- coding: utf-8 -*-
import io, sys, struct, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
env = UnityPy.load(GAME + "\\sharedassets2.assets")
want = {9254, 9258, 9112}
for o in env.objects:
    if o.path_id in want and o.type.name == "MonoBehaviour":
        raw = o.get_raw_data()
        print("\n==== path", o.path_id, "size", len(raw))
        print("  hex:", raw[:64].hex(" "))
        # 找可打印串
        strs = re.findall(rb"[\x20-\x7e]{3,}", raw)
        print("  ascii:", [s.decode() for s in strs[:8]])
        u = raw.decode("utf-16-le", "ignore")
        print("  utf16片段:", repr(u[:40]))
        # 前若干 int32
        ints = struct.unpack_from("<%di" % min(12, len(raw) // 4), raw, 0)
        print("  ints:", ints)
