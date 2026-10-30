# -*- coding: utf-8 -*-
import io, sys, struct, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
env = UnityPy.load(GAME + "\\sharedassets2.assets")
for o in env.objects:
    if o.path_id == 7482 and o.type.name == "MonoBehaviour":
        raw = o.get_raw_data()
        print("size", len(raw))
        for k in range(0, min(len(raw), 320), 32):
            chunk = raw[k:k + 32]
            print("%04d  %-96s  %s" % (k, chunk.hex(" "), re.sub(rb"[^\x20-\x7e]", b".", chunk).decode()))
        # 解析前两个字符串位置
        print("\nints:", struct.unpack_from("<12i", raw, 0))
