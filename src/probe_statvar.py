# -*- coding: utf-8 -*-
"""把 PositionEventData 的 (op, id1, id2) 翻成「属性 比较 值」。

链路：StatGroupVariable(pathID) -> List<StatValueReference> -> checkType/constant/GameStat(pathID) -> _name
GameStat 资产前三个字段：int _type / int _property / string _name
"""
import io, sys, struct
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = ("resources.assets", "sharedassets2.assets")
OPS = {0: "=", 1: "≠", 2: "<", 3: "≤", 4: ">", 5: "≥"}


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


def read_cond(r):
    note = r.string()
    logic = r.i32()
    n = r.i32()
    if n < 0 or n > 60:
        raise ValueError("items")
    items = []
    for _ in range(n):
        op = r.i32()
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
    cnt = r.i32()
    if 0 <= cnt <= 40:
        for _ in range(cnt):
            read_cond(r); r.i32()
        if r.i == len(raw):
            return {"name": name, "dev": dev, "cfg": cfg[1], "toggle": toggle,
                    "active": active, "rate": rate, "items": []}
    raise ValueError("layout")


def statvar(raw):
    """StatGroupVariable: int _groupType, List<StatValueReference>"""
    r = R(raw)
    r.pptr()            # m_GameObject
    r.pptr()            # m_Script
    nm = r.string()     # m_Name
    group = r.i32()
    cnt = r.i32()
    vals = []
    for _ in range(cnt):
        ct = r.i32()
        const = r.i32()
        stat = r.pptr()
        rel = r.pptr()
        flag = r.pptr()
        r.i32(); r.i32()          # randomMin/Max
        for _k in range(4):       # book, misc, specialItem, talentData
            r.pptr()
        sg = r.pptr()
        neg = r.u8(); r.align()
        r.pptr()                  # gameTime
        r.pptr()                  # upgradeItemData
        r.pptr()                  # bookCollection
        r.pptr()                  # libraryAchieve
        r.pptr()                  # condition
        vals.append({"check": ct, "const": const, "stat": stat[1], "flag": flag[1],
                     "group": sg[1], "neg": neg})
    return {"name": nm, "group": group, "vals": vals, "consumed": r.i, "size": len(raw)}


def gamestat_name(raw):
    r = R(raw)
    r.pptr(); r.pptr()
    nm = r.string()   # m_Name
    r.i32(); r.i32()  # _type, _property
    v = r.string()    # _name
    return nm, v


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
        print(f, "对象", len(idx))
    allraw = list(idx.values())

    # 找 Alchemy_Work_E_01
    ped = None
    for (f, pid), raw in idx.items():
        for we in (False, True):
            try:
                d = read_ped(raw, we)
            except Exception:
                continue
            if d["name"] == "Alchemy_Work_E_01":
                ped = d; print("找到 PED:", f, pid, d["dev"], d["active"])
                break
        if ped:
            break
    if not ped:
        print("没找到样本"); return

    # 解析条件里的两个变量
    for op, a, b in ped["active"]["items"]:
        print("\n条件 op=%s (%d) :" % (OPS.get(op), op))
        for pid in (a, b):
            raw = None
            for (f, q), r0 in idx.items():
                if q == pid:
                    raw = r0; fn = f; break
            if raw is None:
                print("   变量", pid, "不在已载入文件"); continue
            try:
                sv = statvar(raw)
            except Exception as e:
                print("   变量", pid, "解失败", e, "raw名未知"); continue
            print("   变量", pid, "name=%r group=%s 项=%s consumed=%d/%d" %
                  (sv["name"], sv["group"], sv["vals"], sv["consumed"], sv["size"]))
            for v in sv["vals"]:
                if v["stat"]:
                    for (f2, q2), r2 in idx.items():
                        if q2 == v["stat"]:
                            try:
                                print("      → 属性资产:", gamestat_name(r2))
                            except Exception as e:
                                print("      → 属性名解失败", e)
                            break


if __name__ == "__main__":
    main()
