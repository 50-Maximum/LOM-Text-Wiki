# -*- coding: utf-8 -*-
"""严格按 externals 解析 PPtr 的 fileID，再取条件编号的中文要求。
用于验证：条件里的两个操作数到底是什么类、什么名字。"""
import io, sys, os, struct, gzip, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

WIKI = r"D:\LegendOfMortal Wiki"
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
LIB = os.path.join(WIKI, "data", "mod_res", "LOMAssistant.conditions.json.gz")
FILES = ["globalgamemanagers.assets", "resources.assets", "sharedassets2.assets", "sharedassets0.assets", "sharedassets1.assets"]
OPS = {0: "=", 1: "≠", 2: "<", 3: "≤", 4: ">", 5: "≥"}


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


lib = json.loads(gzip.open(LIB, "rb").read().decode("utf-8"))
SW, CD = lib["Switches"], lib["Conditions"]

gm = UnityPy.load(os.path.join(GAME, "globalgamemanagers.assets"))
scripts = {}
for o in gm.objects:
    if o.type.name == "MonoScript":
        try:
            d = o.read()
            scripts[o.path_id] = getattr(d, "m_ClassName", "") or getattr(d, "m_Name", "")
        except Exception:
            pass

EXTERNALS, OBJS = {}, {}
for f in FILES:
    p = os.path.join(GAME, f)
    if not os.path.exists(p):
        continue
    env = UnityPy.load(p)
    af = env.files[p]
    ext = getattr(af, "externals", []) or []
    EXTERNALS[f] = [os.path.basename(str(getattr(e, "path", e)).replace("\\", "/")) for e in ext]
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        r = R(raw); r.pptr(); r.i32(); fid, spid = r.pptr()
        OBJS[(f, o.path_id)] = (scripts.get(spid, "?"), raw)

print("外部引用表 sharedassets2:", EXTERNALS.get("sharedassets2.assets"))


def resolve(cur, fid, pid):
    if fid == 0:
        return OBJS.get((cur, pid))
    ext = EXTERNALS.get(cur) or []
    if 1 <= fid <= len(ext):
        return OBJS.get((ext[fid - 1], pid))
    return None


def obj_name(cls, raw):
    try:
        r = R(raw); r.pptr(); r.i32(); r.pptr()
        return r.string()
    except Exception:
        return ""


def text_of(cls, raw):
    nm = obj_name(cls, raw)
    v = SW.get(nm) or CD.get(nm)
    if isinstance(v, list):
        v = "、".join(v)
    if not v:
        return ""
    s = str(v)
    for a, b in ((" 需>=", "≥"), (" 需<=", "≤"), (" 需>", "＞"), (" 需<", "＜"), (" 需=", "＝"), (" 需", "")):
        s = s.replace(a, b)
    return s


def read_ped(cur, raw):
    r = R(raw); r.pptr(); r.i32(); r.pptr()
    name = r.string(); dev = r.string()
    cfg = r.pptr(); tog = r.u8(); r.align()
    act_note = r.string(); logic = r.i32(); n = r.i32()
    items = []
    for _ in range(n):
        op = r.i32(); v1 = r.pptr(); v2 = r.pptr()
        items.append((op, v1, v2))
    rate = r.i32(); cnt = r.i32()
    return {"name": name, "dev": dev, "cfg": cfg, "tog": tog, "logic": logic,
            "items": items, "rate": rate, "arr": cnt, "end": r.i == len(raw)}


found = 0
for (f, p), (cls, raw) in OBJS.items():
    if cls != "PositionEventData":
        continue
    d = read_ped(f, raw)
    if d["name"] != "Alchemy_Work_E_01":
        continue
    print("\nPED", d["name"], "dev", d["dev"], "rate", d["rate"], "exact", d["end"])
    for op, (f1, p1), (f2, p2) in d["items"]:
        for tag, (ff, pp) in (("v1", (f1, p1)), ("v2", (f2, p2))):
            got = resolve(f, ff, pp)
            if not got:
                print("   %s fileID=%s pathID=%s -> 未找到" % (tag, ff, pp)); continue
            c2, raw2 = got
            print("   %s -> %-22s %-18s %s" % (tag, c2, obj_name(c2, raw2)[:18], text_of(c2, raw2)[:40]))
    found += 1
    break
