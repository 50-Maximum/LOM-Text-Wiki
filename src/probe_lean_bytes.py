# -*- coding: utf-8 -*-
"""调试 LeanPhrase 原始字节：确认字段布局（data/entries）。"""
import io, os, struct, sys, binascii
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
gm = UnityPy.load(os.path.join(GAME, "globalgamemanagers.assets"))
scripts = {}
for o in gm.objects:
    if o.type.name == "MonoScript":
        try:
            d = o.read()
            scripts[o.path_id] = getattr(d, "m_ClassName", "") or getattr(d, "m_Name", "")
        except Exception:
            pass

def head(b, n=64):
    return binascii.hexlify(b[:n]).decode()

found = 0
for f in ["level0"] + [x for x in os.listdir(GAME) if x.endswith(".assets")]:
    p = os.path.join(GAME, f)
    if not os.path.exists(p):
        continue
    try:
        env = UnityPy.load(p)
    except Exception:
        continue
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        if len(raw) < 24:
            continue
        fid, spid = struct.unpack_from("<iq", raw, 4)
        cls = scripts.get(spid, "")
        if cls != "LeanPhrase":
            continue
        found += 1
        print("\n文件 %s path_id %s 长度 %d" % (f, o.path_id, len(raw)))
        print("  name:", end=" ")
        try:
            print(repr(o.peek_name()))
        except Exception as e:
            print("失败", e)
        print("  head:", head(raw, 72))
        # 尝试：跳过 gameobject/align/script 后按 i32(int) + i32(count)
        off = 4 + 12 + 8  # 粗算
        for skip in (16, 20, 24, 28):
            try:
                d = struct.unpack_from("<i", raw, skip)[0]
                n = struct.unpack_from("<i", raw, skip + 4)[0]
                print("   skip=%2d data=%d count=%d" % (skip, d, n))
            except Exception:
                pass
        if found >= 3:
            sys.exit(0)
print("命中 LeanPhrase", found)
