# -*- coding: utf-8 -*-
"""把单章大文件按场景切成约 60KB 的批次。"""
import os, re

SRC = r"D:\LegendOfMortal Wiki\data\read"
def split_chapter(name, target=60000):
    p = os.path.join(SRC, name + ".txt")
    s = open(p, encoding="utf-8").read()
    parts = re.split(r"(?=\n===== )", s)
    chunks, cur, size = [], [], 0
    for seg in parts:
        if not seg.strip():
            continue
        seg_size = len(seg.encode("utf-8"))
        if cur and size + seg_size > target:
            chunks.append("".join(cur))
            cur, size = [], 0
        cur.append(seg)
        size += seg_size
    if cur:
        chunks.append("".join(cur))
    for i, ch in enumerate(chunks, 1):
        fn = os.path.join(SRC, "%s.part%d.txt" % (name, i))
        open(fn, "w", encoding="utf-8").write(ch)
    print(name, "parts:", len(chunks), [round(len(c.encode("utf-8"))/1024) for c in chunks], "KB")

for ch in ("第2章", "第3章", "第4章", "第5章", "第6章", "第7章", "第8章", "支线", "其他"):
    try:
        split_chapter(ch)
    except FileNotFoundError:
        print("missing", ch)
