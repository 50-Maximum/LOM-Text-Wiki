# -*- coding: utf-8 -*-
"""诊断：按 externals 正确解析 MonoScript 类名，找 LeanPhrase / LeanLocalization 对象在哪个文件。"""
import io, os, struct, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = [f for f in os.listdir(GAME) if f.endswith(".assets")]

class R:
    def __init__(self, b, i=0): self.b, self.i = b, i
    def i32(self):
        v = struct.unpack_from("<i", self.b, self.i)[0]; self.i += 4; return v
    def i64(self):
        v = struct.unpack_from("<q", self.b, self.i)[0]; self.i += 8; return v
    def pptr(self):
        f = self.i32(); p = self.i64(); return (f, p)

gm = UnityPy.load(os.path.join(GAME, "globalgamemanagers.assets"))
scripts = {}
for o in gm.objects:
    if o.type.name == "MonoScript":
        try:
            d = o.read()
            scripts[o.path_id] = getattr(d, "m_ClassName", "") or getattr(d, "m_Name", "")
        except Exception:
            pass
print("MonoScript 数", len(scripts))

# 全部 MonoScript 名里含 Lean 的
lean = sorted({v for v in scripts.values() if "Lean" in (v or "")})
print("含 Lean 的脚本类:", lean[:20])

EXTERNAL, OBJS = {}, {}
for f in FILES:
    p = os.path.join(GAME, f)
    try:
        env = UnityPy.load(p)
        af = env.files[p]
    except Exception:
        continue
    EXTERNAL[f] = [os.path.basename(str(getattr(e, "path", e)).replace("\\", "/"))
                   for e in (getattr(af, "externals", []) or [])]
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        r = R(raw); r.pptr(); r.i32(); fid, spid = r.pptr()
        OBJS[(f, o.path_id)] = (fid, spid, raw)

def resolve(cur, fid, spid):
    if fid == 0:
        return scripts.get(spid)
    ext = EXTERNAL.get(cur) or []
    if 1 <= fid <= len(ext):
        # MonoScript 也可能在外部文件里
        return scripts.get(spid) or ("ext:" + ext[fid - 1])
    return None

cnt = collections.Counter()
for (f, pid), (fid, spid, raw) in OBJS.items():
    cls = resolve(f, fid, spid) or "?"
    if "Lean" in str(cls):
        cnt[(f, cls)] += 1
print("\nLean 相关对象分布:", cnt.most_common(10))
print("总 MonoBehaviour", len(OBJS))
