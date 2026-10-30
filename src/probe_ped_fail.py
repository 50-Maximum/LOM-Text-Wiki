# -*- coding: utf-8 -*-
"""诊断：1) 哪些 PositionEventData 解不出、卡在哪；2) 未映射的名称与现有剧本名的差异。"""
import io, sys, os, struct, sqlite3, collections, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = ["globalgamemanagers.assets", "resources.assets", "sharedassets2.assets"]


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
        s = self.b[self.i:self.i + n]; self.i += n; self.align()
        return s.decode("utf-8", "replace")
    def u8(self):
        v = self.b[self.i]; self.i += 1; return v


scripts = {}
gm = UnityPy.load(os.path.join(GAME, "globalgamemanagers.assets"))
for o in gm.objects:
    if o.type.name == "MonoScript":
        try:
            d = o.read()
            scripts[o.path_id] = getattr(d, "m_ClassName", "") or getattr(d, "m_Name", "")
        except Exception:
            pass

peds = []
for f in FILES:
    p = os.path.join(GAME, f)
    env = UnityPy.load(p)
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        r = R(raw); r.pptr(); r.i32(); fid, spid = r.pptr()
        if scripts.get(spid) == "PositionEventData":
            peds.append((f, o.path_id, raw))
print("PositionEventData:", len(peds))

ok, fail = 0, []
for f, pid, raw in peds:
    try:
        r = R(raw); r.pptr(); r.i32(); r.pptr()
        name = r.string(); dev = r.string()
        r.pptr(); r.u8(); r.align()
        r.string(); r.i32()
        n1 = r.i32()
        if not (0 <= n1 <= 40):
            raise ValueError("n1")
        for _ in range(n1):
            r.i32(); r.pptr(); r.pptr()
        r.i32()
        n2 = r.i32()
        if not (0 <= n2 <= 40):
            raise ValueError("n2")
        for _ in range(n2):
            r.string(); r.i32(); m = r.i32()
            for _ in range(m):
                r.i32(); r.pptr(); r.pptr()
            r.i32()
        if r.i != len(raw):
            raise ValueError("size %d/%d" % (r.i, len(raw)))
        ok += 1
    except Exception as e:
        fail.append((f, pid, len(raw), name if 'name' in dir() else "", str(e)))

print("完整解出:", ok, " 失败:", len(fail))
c = collections.Counter(str(x[4]).split()[0] for x in fail)
print("失败原因:", c.most_common())
for x in fail[:10]:
    print("   %-22s %-6d size %-4d name=%-24r %s" % x)

# 未映射：看 door/forge/mall 现有剧本名
cb = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for pre in ("door_%", "forge_%", "mall_%", "fortress_%", "center_%", "craft_%", "kitchen_%", "pharmacy_%"):
    rows = [r[0] for r in cb.execute("select script from scenes where script like ? order by script limit 12", (pre,))]
    print("\n", pre, len(rows), rows)
