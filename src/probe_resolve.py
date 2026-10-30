# -*- coding: utf-8 -*-
"""正确解析 PPtr 的 fileID：用 assets 文件的 externals 表把 fileID 映射到具体文件，
再确认 PositionEventData 条件里的 _value1/_value2 到底指向什么类。"""
import io, sys, os, struct
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = ("resources.assets", "sharedassets2.assets", "sharedassets0.assets", "sharedassets1.assets")


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


envs = {}
for f in FILES:
    p = os.path.join(GAME, f)
    if not os.path.exists(p):
        continue
    envs[f] = UnityPy.load(p)

for f, env in envs.items():
    print("\n", f, "files:", list(env.files)[:3] if hasattr(env, "files") else "?")
    for name, af in (env.files.items() if hasattr(env, "files") else []):
        ext = getattr(af, "externals", None)
        if ext:
            print("   externals of", name)
            for i, e in enumerate(ext[:6]):
                print("     [%d] %s" % (i + 1, getattr(e, "path", e)))
        break

# MonoScript 表
gm = UnityPy.load(os.path.join(GAME, "globalgamemanagers.assets"))
scripts = {}
for o in gm.objects:
    if o.type.name == "MonoScript":
        try:
            d = o.read()
            scripts[o.path_id] = getattr(d, "m_ClassName", "") or getattr(d, "m_Name", "")
        except Exception:
            pass

# 建 pathID -> [(file, class)] 索引，但不靠猜 fileID
idx = {}
for f, env in envs.items():
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        r = R(raw)
        r.pptr(); r.i32()
        fid, spid = r.pptr()
        cls = scripts.get(spid, "?")
        idx.setdefault(o.path_id, []).append((f, cls, raw))

for pid in (9254, 9258, 9259, 9181, 9112, 8009):
    print("\npathID", pid, "->")
    for f, cls, raw in idx.get(pid, [])[:4]:
        print("   %-22s %-20s size %d" % (f, cls, len(raw)))
