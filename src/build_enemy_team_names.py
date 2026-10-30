# -*- coding: utf-8 -*-
"""从 level0 直接抽 LeanLocalization 的字符串表：EnemyTeam/NNN → 中文名。

资产里的字符串是「int32 长度 + UTF-8 + 4 字节对齐」，所以可以按字节模式扫：
  13 00 00 00 | "EnemyTeam/000" | 3 字节填充 | 长度 | 文本
多语言共存，只取值里含中文的那份。
"""
import io, json, os, re, struct, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from opencc import OpenCC
cc = OpenCC("t2s")
BASE = r"D:\LegendOfMortal Wiki"
P = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\level0"
b = open(P, "rb").read()
CJK = re.compile(r"[\u4e00-\u9fff]")

def read_str(buf, off):
    """读「长度 + UTF-8 + 对齐」，返回 (文本, 下一个偏移)。"""
    if off + 4 > len(buf):
        return None, off
    n = struct.unpack_from("<i", buf, off)[0]
    if n < 0 or n > 4000 or off + 4 + n > len(buf):
        return None, off
    raw = buf[off + 4: off + 4 + n]
    nxt = off + 4 + n
    nxt = (nxt + 3) & ~3
    return raw.decode("utf-8", "replace"), nxt

pairs = collections.defaultdict(dict)
pos = 0
found = 0
while True:
    i = b.find(b"EnemyTeam/", pos)
    if i < 0:
        break
    pos = i + 1
    if i < 4 or struct.unpack_from("<i", b, i - 4)[0] != 13:
        continue
    key = b[i:i + 13].decode("utf-8", "replace")
    val, _ = read_str(b, i + 13 + 3)  # 13 字节后补到 16
    if not val:
        continue
    found += 1
    if CJK.search(val):
        pairs[key][val] = 1

out = {}
for k, vals in pairs.items():
    v = max(vals, key=len)
    out[k] = cc.convert(v)

print("命中 EnemyTeam 键 %d（含中文的 %d）" % (found, len(out)))
for k in list(out)[:12]:
    print("   %-18s %s" % (k, out[k]))

json.dump(out, open(os.path.join(BASE, "data", "enemy_team_names.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
