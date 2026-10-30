# -*- coding: utf-8 -*-
"""解 LeanPhrase 本地化表（含 level0 场景）：键 → 各语言文本。

之前只扫 *.assets 漏掉了 level0（场景文件），而「EnemyTeam/」这类键就存在那里。
"""
import io, os, struct, json, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

WIKI = r"D:\LegendOfMortal Wiki"
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = [f for f in os.listdir(GAME) if f.endswith(".assets")] + ["level0"]

class R:
    def __init__(self, b, i=0): self.b, self.i = b, i
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

out, fails, langs = {}, 0, collections.Counter()
for f in FILES:
    p = os.path.join(GAME, f)
    if not os.path.exists(p):
        continue
    try:
        env = UnityPy.load(p)
    except Exception:
        continue
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
            r = R(raw)
            r.pptr(); r.i32(); fid, spid = r.pptr()
            if scripts.get(spid) != "LeanPhrase":
                continue
            try:
                key = o.peek_name() or ""
            except Exception:
                key = ""
            data = r.i32()
            n = r.i32()
            if not (0 <= n <= 60):
                raise ValueError("n")
            ents = {}
            for _ in range(n):
                lang = r.string()
                text = r.string()
                r.pptr()
                langs[lang] += 1
                if text:
                    ents[lang] = text
            if key and ents:
                out.setdefault(key, {}).update(ents)
        except Exception:
            fails += 1
            continue

json.dump(out, open(os.path.join(WIKI, "data", "lean_phrases.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("LeanPhrase 键 %d，失败 %d" % (len(out), fails))
print("语言标记:", langs.most_common(6))
print("含 EnemyTeam 的键:", sum(1 for k in out if k.startswith("EnemyTeam/")))
for k in [k for k in out if k.startswith("EnemyTeam/")][:8]:
    print("   %-26s %s" % (k, list(out[k].items())[:2]))
