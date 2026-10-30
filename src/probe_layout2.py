# -*- coding: utf-8 -*-
"""换一种假设再试：_activeCondition 是指向资产的条件对象（PPtr），不是内联结构。
同时把条件对象、StatGroupVariable 都当资产来解，看能不能解出属性名。"""
import io, sys, struct
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = ("resources.assets", "sharedassets2.assets")


class R:
    def __init__(self, b, i=0):
        self.b, self.i = b, i

    def u8(self):
        v = self.b[self.i]; self.i += 1; return v

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


def ped_b(raw):
    """_activeCondition 当 PPtr"""
    r = R(raw)
    r.pptr()
    r.u8(); r.align()
    r.pptr()
    nm = r.string()
    dev = r.string()
    cfg = r.pptr()
    tog = r.u8(); r.align()
    act = r.pptr()
    rate = r.i32()
    cnt = r.i32()
    if not (0 <= cnt <= 40):
        raise ValueError("cnt")
    items = []
    for _ in range(cnt):
        c = r.pptr(); rr = r.i32()
        if not (0 <= rr <= 100):
            raise ValueError("rate")
        items.append((c[1], rr))
    if r.i != len(raw):
        raise ValueError("size")
    return {"name": nm, "dev": dev, "act": act[1], "rate": rate, "items": items}


def cond_asset(raw):
    """string _devNote, int _logicOp, List<StatCompareItem>{int op, PPtr v1, PPtr v2}"""
    r = R(raw)
    r.pptr(); r.pptr()
    nm = r.string()
    dev = r.string()
    logic = r.i32()
    n = r.i32()
    if not (0 <= n <= 40):
        raise ValueError("n")
    its = []
    for _ in range(n):
        op = r.i32()
        v1 = r.pptr(); v2 = r.pptr()
        its.append((op, v1[1], v2[1]))
    return {"name": nm, "dev": dev, "logic": logic, "items": its, "i": r.i, "size": len(raw)}


def main():
    idx = {}
    for f in FILES:
        env = UnityPy.load(GAME + "\\" + f)
        for o in env.objects:
            if o.type.name == "MonoBehaviour":
                try:
                    idx[(f, o.path_id)] = o.get_raw_data()
                except Exception:
                    pass
    bypid = {}
    for (f, p), raw in idx.items():
        bypid.setdefault(p, []).append((f, raw))
    print("对象", len(idx))

    good = []
    for (f, p), raw in idx.items():
        try:
            d = ped_b(raw)
        except Exception:
            continue
        good.append((f, p, d))
    print("按 PPtr 布局完整解出:", len(good))

    for f, p, d in good[:10]:
        print("\n %s %s name=%r dev=%r rate=%s items=%d" % (f, p, d["name"], d["dev"][:30], d["rate"], len(d["items"])))
        if d["act"]:
            for ff, rr in bypid.get(d["act"], []):
                try:
                    ca = cond_asset(rr)
                    print("   条件资产 %s: dev=%r logic=%s items=%s (%d/%d)" %
                          (ff, ca["dev"][:20], ca["logic"], ca["items"][:3], ca["i"], ca["size"]))
                except Exception as e:
                    print("   条件资产解失败", e)


if __name__ == "__main__":
    main()
