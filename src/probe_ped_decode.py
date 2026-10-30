# -*- coding: utf-8 -*-
"""PositionEventData 字节解码可行性：试两种 MonoBehaviour 头布局，要求解完整份字节。"""
import io, sys, struct, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"


class R:
    def __init__(self, b):
        self.b, self.i = b, 0

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
        self.i += n
        self.align()
        return s.decode("utf-8", "replace")


def read_cond(r):
    note = r.string()
    if len(note) > 300:
        raise ValueError("cond note")
    logic = r.i32()
    if logic not in (0, 1):
        raise ValueError("logic")
    n = r.i32()
    if n < 0 or n > 60:
        raise ValueError("items")
    items = []
    for _ in range(n):
        op = r.i32()
        if op < 0 or op > 5:
            raise ValueError("op")
        v1 = r.pptr(); v2 = r.pptr()
        items.append((op, v1[1], v2[1]))
    return {"note": note, "logic": logic, "items": items}


def read_ped(raw, with_enabled):
    r = R(raw)
    r.pptr()
    if with_enabled:
        r.u8(); r.align()
    r.pptr()
    name = r.string()
    dev = r.string()
    cfg = r.pptr()
    toggle = r.u8(); r.align()
    if toggle not in (0, 1):
        raise ValueError("bool")
    active = read_cond(r)
    rate = r.i32()
    if rate < 0 or rate > 100:
        raise ValueError("rate")
    cnt = r.i32()
    if cnt < 0 or cnt > 40:
        raise ValueError("arr")
    arr = []
    for _ in range(cnt):
        c = read_cond(r)
        rr = r.i32()
        if rr < 0 or rr > 100:
            raise ValueError("irate")
        arr.append((c, rr))
    if r.i != len(raw):
        raise ValueError("size %d/%d" % (r.i, len(raw)))
    return {"name": name, "dev": dev, "cfg": cfg[1], "toggle": toggle,
            "active": active, "rate": rate, "items": arr}


def main():
    ok = []
    tried = 0
    for f in ("resources.assets", "sharedassets2.assets"):
        env = UnityPy.load(GAME + "\\" + f)
        for o in env.objects:
            if o.type.name != "MonoBehaviour":
                continue
            tried += 1
            try:
                raw = o.get_raw_data()
            except Exception:
                continue
            for we in (False, True):
                try:
                    d = read_ped(raw, we)
                except Exception:
                    continue
                d["_file"] = f; d["_we"] = we
                ok.append(d)
                break
        print(f, "通过", len(ok))
    print("尝试", tried, " 完整解出", len(ok))
    for d in ok[:8]:
        print("\n name=%r dev=%r cfg=%s toggle=%s rate=%s items=%d" %
              (d["name"][:20], d["dev"][:50], d["cfg"], d["toggle"], d["rate"], len(d["items"])))
        print("   active:", d["active"]["note"][:50], d["active"]["items"][:2])
    print("\n布局统计:", collections.Counter(d["_we"] for d in ok))


if __name__ == "__main__":
    main()
