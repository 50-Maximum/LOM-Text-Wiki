# -*- coding: utf-8 -*-
"""用已知字段（StoryMappingItem: Key/Value 两个字符串）验证头部偏移是否算对。
若 8009 能整份解成两个字符串，说明 PED 前缀解析正确，问题只在尾部结构。"""
import io, sys, struct
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"


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
        s = self.b[self.i:self.i + n]
        self.i += n; self.align()
        return s.decode("utf-8", "replace")


def mapping_item(raw, with_enabled):
    r = R(raw)
    r.pptr()
    if with_enabled:
        r.i32()
    r.pptr()
    name = r.string()
    key = r.string()
    val = r.string()
    return name, key, val, r.i == len(raw), r.i, len(raw)


env = UnityPy.load(GAME + "\\sharedassets2.assets")
targets = {8009, 8010, 8011, 9254, 9258}
for o in env.objects:
    if o.path_id in targets and o.type.name == "MonoBehaviour":
        raw = o.get_raw_data()
        print("\n== path", o.path_id, "size", len(raw))
        for we in (False, True):
            try:
                nm, k, v, exact, i, sz = mapping_item(raw, we)
                print("   mapping(we=%s): name=%r key=%r value=%r exact=%s (%d/%d)" % (we, nm[:20], k[:30], v[:30], exact, i, sz))
            except Exception as e:
                print("   mapping(we=%s) 失败: %s" % (we, e))
