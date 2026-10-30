# -*- coding: utf-8 -*-
"""解 LeanLocalization 的 LeanPhrase：键（GameObject 名）→ 各语言文本。

LeanPhrase 结构（LeanSource 的 MonoBehaviour 反序列化）：
  m_GameObject PPtr / m_Enabled int / m_Script PPtr
  data: int（0=Text,1=Object,2=Sprite）
  entries: int 数量 → 每条 { Language: string, Text: string, Object: PPtr }

输出 data/lean_phrases.json：{键: {语言: 文本}}
"""
import io, os, struct, json, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

WIKI = r"D:\LegendOfMortal Wiki"
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = [f for f in os.listdir(GAME) if f.endswith(".assets")]

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

out, fails, langs = {}, 0, collections.Counter()
for f in FILES:
    p = os.path.join(GAME, f)
    try:
        env = UnityPy.load(p)
    except Exception:
        continue
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        try:
            r = R(raw)
            r.pptr(); r.i32(); fid, spid = r.pptr()
            if scripts.get(spid) != "LeanPhrase":
                continue
            key = ""
            try:
                key = o.peek_name() or ""
            except Exception:
                key = ""
            data = r.i32()
            n = r.i32()
            if not (0 <= n <= 50):
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
                out[key] = ents
        except Exception:
            fails += 1
            continue

json.dump(out, open(os.path.join(WIKI, "data", "lean_phrases.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("LeanPhrase 键 %d，解析失败 %d" % (len(out), fails))
print("语言标记:", langs.most_common(8))
for k in list(out)[:8]:
    v = out[k]
    print("   %-28s %s" % (k, str(list(v.items())[:2])[:90]))
