# -*- coding: utf-8 -*-
"""对 object 7482 做穷举：在哪个偏移开始是数组、每个条目多大，能让整份字节刚好解完且引用都存在。"""
import io, sys, struct
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
env = UnityPy.load(GAME + "\\sharedassets2.assets")
raw = None
pids = set()
for o in env.objects:
    if o.type.name == "MonoBehaviour":
        pids.add(o.path_id)
        if o.path_id == 7482:
            raw = o.get_raw_data()
print("对象 7482 尺寸", len(raw), " 已知 pathID 数", len(pids))


def pptr_at(buf, i):
    f = struct.unpack_from("<i", buf, i)[0]
    p = struct.unpack_from("<q", buf, i + 4)[0]
    return f, p


def try_items(start, stride, n):
    """读 n 个 28 字节条目：op, v1, v2（op 在条目前）"""
    out = []
    i = start
    for _ in range(n):
        if i + stride > len(raw):
            return None
        if stride == 28:
            op = struct.unpack_from("<i", raw, i)[0]
            f1, p1 = pptr_at(raw, i + 4)
            f2, p2 = pptr_at(raw, i + 16)
            if not (0 <= op <= 5):
                return None
            if p1 and p1 not in pids:
                return None
            if p2 and p2 not in pids:
                return None
            out.append((op, p1, p2))
        i += stride
    return out


found = []
for start in range(64, 140, 4):
    for stride in (28, 16, 12, 32, 24):
        for n in range(0, 9):
            end = start + stride * n
            if end != len(raw):
                continue
            got = try_items(start, stride, n)
            if got is None:
                continue
            found.append((start, stride, n, got))
print("候选:", len(found))
for s, st, n, got in found[:10]:
    print("  start=%d stride=%d n=%d -> %s" % (s, st, n, got))
