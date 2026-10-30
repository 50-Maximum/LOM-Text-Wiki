# -*- coding: utf-8 -*-
"""按导语里的明确方位，把能从「其他」挪出的地点补进区域表（只用导语明说的证据）。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

# 一级证据：导语直接点明所属州府/山门
EXTRA = {
    # 川蜀
    "川蜀": "川蜀", "山神龛": "川蜀", "石灰沱": "川蜀",
    # 巴渝
    "夔州巫山县衙大牢": "巴渝", "黄龙泉": "巴渝",
    # 荆湖
    "六道峡": "荆湖", "春雨楼": "荆湖", "谭州腾云山": "荆湖", "腾云寨": "荆湖",
    "锦绣轩": "荆湖", "香露池": "荆湖",
    # 关中陇右
    "孟章厢房": "关中陇右", "监兵厢房": "关中陇右", "陵光厢房": "关中陇右",
    "插香台": "关中陇右", "朽木桥": "关中陇右",
    # 中原
    "般若院": "中原", "红岭": "中原", "梁家医馆": "中原",
    # 西南夷
    "松烟阁": "西南夷",
}

block = "\nREGION_MAP.update(%r)\n" % (EXTRA,)
if "REGION_MAP.update(" not in s:
    anchor = "\n\ndef _region_of("
    assert anchor in s, "_region_of 定义未找到"
    s = s.replace(anchor, block + anchor, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已补 %d 条区域归属" % len(EXTRA))
else:
    s2 = re.sub(r"REGION_MAP\.update\(\{[^}]*\}\)",
                "REGION_MAP.update(%r)" % (EXTRA,), s, count=1)
    open(P, "w", encoding="utf-8").write(s2)
    print("已替换区域补丁（%d 条）" % len(EXTRA))
