# -*- coding: utf-8 -*-
"""看 9254 这类 pathID 在各文件里到底是什么对象（打印尺寸与 m_Name）。"""
import io, sys, struct
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
TARGETS = {9254, 9258, 9259, 9181, 9112}
FILES = ("resources.assets", "sharedassets2.assets", "sharedassets0.assets")


def head(raw):
    b = raw
    n = struct.unpack_from("<i", b, 24)[0] if len(b) > 28 else -1
    if 0 <= n <= 200 and 28 + n <= len(b):
        s = b[28:28 + n].decode("utf-8", "replace")
    else:
        s = ""
    return s


for f in FILES:
    try:
        env = UnityPy.load(GAME + "\\" + f)
    except Exception as e:
        print(f, "打开失败", e); continue
    for o in env.objects:
        if o.path_id in TARGETS and o.type.name == "MonoBehaviour":
            try:
                raw = o.get_raw_data()
            except Exception:
                continue
            print("%-22s path %-6d size %4d  m_Name=%r" % (f, o.path_id, len(raw), head(raw)[:40]))
