# -*- coding: utf-8 -*-
"""解出 CombatLevel / BattleLevel 的关卡编号与描述（_desc），补齐「战斗名」。

CombatLevel 序列化顺序：_desc(string) → 其余 PPtr/bool/数组
对象头部：m_GameObject PPtr → m_Enabled int → m_Script PPtr → m_Name string → 字段
所以第 1 个字符串 = 资源名（关卡编号），第 2 个 = _desc。
"""
import io, os, struct, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

WIKI = r"D:\LegendOfMortal Wiki"
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = [f for f in os.listdir(GAME) if f.endswith(".assets")]
TARGETS = {"CombatLevel", "BattleLevel", "CombatLevelConfig"}

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
        if n < 0 or n > 20000 or self.i + n > len(self.b):
            raise ValueError("str")
        s = self.b[self.i:self.i + n]; self.i += n; self.align()
        return s.decode("utf-8", "replace")

gm = UnityPy.load(os.path.join(GAME, "globalgamemanagers.assets"))
scripts = {}
for o in gm.objects:
    if o.type.name == "MonoScript":
        try:
            d = o.read()
            scripts[o.path_id] = getattr(d, "m_ClassName", "") or getattr(d, "m_Name", "")
        except Exception:
            pass

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
        cls = scripts.get(spid, "")
        if cls in TARGETS:
            OBJS[(f, o.path_id)] = (cls, raw)

print("目标对象", len(OBJS))
out = []
for (f, pid), (cls, raw) in OBJS.items():
    try:
        r = R(raw); r.pptr(); r.i32(); r.pptr()
        name = r.string()
        desc = r.string()
    except Exception:
        continue
    out.append({"cls": cls, "file": f, "name": name, "desc": desc})

from collections import Counter
print("按类:", Counter(x["cls"] for x in out))
has = [x for x in out if x["desc"].strip()]
print("有描述:", len(has), "/", len(out))

json.dump(out, open(os.path.join(WIKI, "data", "combat_levels.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for x in has[:12]:
    print("   %-22s %-8s %s" % (x["name"], x["cls"], x["desc"][:60]))
