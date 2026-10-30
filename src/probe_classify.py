# -*- coding: utf-8 -*-
"""用 globalgamemanagers.assets 里的 MonoScript 表给每个 MonoBehaviour 定类，
再按字段顺序解码 PositionEventData，并在每个 PPtr 处打印目标类，用来核对结构。"""
import io, sys, os, struct, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"


class R:
    def __init__(self, b, i=0):
        self.b, self.i = b, i

    def i32(self):
        v = struct.unpack_from("<i", self.b, self.i)[0]; self.i += 4; return v

    def i64(self):
        v = struct.unpack_from("<q", self.b, self.i)[0]; self.i += 8; return v

    def pptr(self):
        f = self.i32(); p = self.i64(); return (f, p)

    def align(self):
        self.i = (self.i + 3) & ~3

    def string(self):
        n = self.i32()
        if n < 0 or n > 4000 or self.i + n > len(self.b):
            raise ValueError("str")
        s = self.b[self.i:self.i + n]
        self.i += n; self.align()
        return s.decode("utf-8", "replace")

    def u8(self):
        v = self.b[self.i]; self.i += 1; return v


# 1) MonoScript 表
gm = UnityPy.load(os.path.join(GAME, "globalgamemanagers.assets"))
scripts = {}
for o in gm.objects:
    if o.type.name == "MonoScript":
        try:
            d = o.read()
            scripts[o.path_id] = getattr(d, "m_ClassName", "") or getattr(d, "m_Name", "")
        except Exception:
            pass
print("MonoScript 表:", len(scripts))

# 2) 对象索引 + 类名（假设 fileID=1 -> globalgamemanagers）
objs = {}
for f in ("resources.assets", "sharedassets2.assets"):
    env = UnityPy.load(os.path.join(GAME, f))
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        r = R(raw)
        r.pptr()                 # m_GameObject
        r.i32()                  # 4 字节（m_Enabled 之类）
        fid, spid = r.pptr()     # m_Script
        cls = scripts.get(spid, "?") if fid in (0, 1) else "?"
        objs[(f, o.path_id)] = (raw, cls)
from collections import Counter
c = Counter(v[1] for v in objs.values())
print("类名分布 top:", c.most_common(12))
print("PositionEventData 对象数:", c.get("PositionEventData", 0))


def resolve(fid, pid):
    if fid in (0, 1):
        for (f, p), (raw, cls) in objs.items():
            if p == pid:
                return cls, raw, f
    return None, None, None


# 3) 解一个 PED
for (f, p), (raw, cls) in objs.items():
    if cls != "PositionEventData":
        continue
    r = R(raw)
    r.pptr()
    r.i32()
    fid, spid = r.pptr()
    name = r.string()
    if name != "Alchemy_Work_E_01":
        continue
    print("\n=== PED", f, p, name, "size", len(raw))
    dev = r.string()
    print(" _devNote =", repr(dev))
    cf = r.pptr()
    print(" _config ->", cf, resolve(*cf)[0])
    tog = r.u8(); r.align()
    print(" _toggleCondition =", tog)
    # 下一个 PPtr
    pos = r.i
    pf, pp = r.pptr()
    print(" [pos %d] next PPtr ->" % pos, (pf, pp), resolve(pf, pp)[0])
    break
