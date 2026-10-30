# -*- coding: utf-8 -*-
"""抽取地图位置事件（PositionEventData）全部字段。

类名：globalgamemanagers.assets 的 MonoScript 表；PPtr：按各 .assets 的 externals 解析 fileID。
输出 data/position_events.json（433 条）
"""
import io, sys, os, struct, gzip, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

WIKI = r"D:\LegendOfMortal Wiki"
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
LIB = os.path.join(WIKI, "data", "mod_res", "LOMAssistant.conditions.json.gz")
OUT = os.path.join(WIKI, "data", "position_events.json")
FILES = ["globalgamemanagers.assets", "resources.assets", "sharedassets2.assets",
         "sharedassets0.assets", "sharedassets1.assets"]
OPS = {0: "=", 1: "≠", 2: "<", 3: "≤", 4: ">", 5: "≥"}
LOGIC = {0: "且", 1: "或"}


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


def disp(nm):
    if not nm:
        return "?"
    for pre, rep in (("時間_", ""), ("旗標_", "旗标"), ("常數_", ""), ("好感度_", ""),
                     ("技能_", ""), ("貴重品_", ""), ("贵重品_", ""), ("數值_", ""), ("秘笈等級_", "秘笈等级")):
        if nm.startswith(pre):
            return rep + nm[len(pre):]
    return nm


def main():
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

    EXTERNAL, OBJS = {}, {}
    for f in FILES:
        p = os.path.join(GAME, f)
        if not os.path.exists(p):
            continue
        env = UnityPy.load(p)
        af = env.files[p]
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
            OBJS[(f, o.path_id)] = (scripts.get(spid, "?"), raw)
    print("对象:", len(OBJS))

    def resolve(cur, fid, pid):
        if fid == 0:
            return OBJS.get((cur, pid))
        ext = EXTERNAL.get(cur) or []
        if 1 <= fid <= len(ext):
            return OBJS.get((ext[fid - 1], pid))
        return None

    def name_of(raw):
        r = R(raw); r.pptr(); r.i32(); r.pptr()
        return r.string()

    def text_of(raw):
        nm = name_of(raw)
        v = SW.get(nm) or CD.get(nm)
        if isinstance(v, list):
            v = "、".join(v)
        return str(v) if v else ""

    def operand(cur, fid, pid):
        got = resolve(cur, fid, pid)
        if not got:
            return {"disp": "?", "raw": "", "text": ""}
        cls, raw = got
        return {"disp": disp(name_of(raw)), "raw": name_of(raw), "text": text_of(raw)}

    out, bad = [], []
    for (f, p), (cls, raw) in OBJS.items():
        if cls != "PositionEventData":
            continue
        try:
            r = R(raw); r.pptr(); r.i32(); r.pptr()
            name = r.string(); dev = r.string()
            cfg = r.pptr()
            tog = r.u8(); r.align()
            r.string(); logic = r.i32()
            n1 = r.i32()
            if not (0 <= n1 <= 40):
                raise ValueError("n1")
            items = []
            for _ in range(n1):
                op = r.i32(); v1 = r.pptr(); v2 = r.pptr()
                items.append((op, v1, v2))
            rate = r.i32()
            n2 = r.i32()
            if not (0 <= n2 <= 40):
                raise ValueError("n2")
            rates = []
            for _ in range(n2):
                r.string(); r.i32(); m = r.i32()
                its = []
                for _ in range(m):
                    op = r.i32(); v1 = r.pptr(); v2 = r.pptr()
                    its.append((op, v1, v2))
                rr = r.i32()
                rates.append((its, rr))
            if r.i != len(raw):
                raise ValueError("size")
        except Exception as e:
            bad.append((f, p, str(e)))
            continue

        cm = resolve(f, cfg[0], cfg[1])
        key = val = ""
        if cm and cm[0] == "StoryMappingItem":
            rr = R(cm[1]); rr.pptr(); rr.i32(); rr.pptr(); rr.string()
            key, val = rr.string(), rr.string()

        def rows(its):
            res = []
            for op, v1, v2 in its:
                a = operand(f, v1[0], v1[1])
                b = operand(f, v2[0], v2[1])
                simple = (a["raw"].startswith(("時間_", "旗標_", "常數_", "好感度_", "技能_", "數值_", "貴重品_", "秘笈等級_"))
                          or b["raw"].startswith(("時間_", "常數_", "旗標_")))
                if simple or not a["text"]:
                    res.append("%s %s %s" % (a["disp"], OPS.get(op, op), b["disp"]))
                else:
                    res.append(a["text"])
            return res

        out.append({"name": name, "dev": dev, "key": key, "value": val, "rate": rate,
                    "logic": LOGIC.get(logic, logic), "cond": rows(items),
                    "rates": [{"rate": rr, "cond": rows(it)} for it, rr in rates],
                    "file": f})

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("解出 %d，失败 %d → %s" % (len(out), len(bad), OUT))
    for b in bad[:5]:
        print("   失败", b)


if __name__ == "__main__":
    main()
