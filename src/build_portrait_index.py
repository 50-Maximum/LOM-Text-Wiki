# -*- coding: utf-8 -*-
"""建立 角色 id -> 立绘文件 的索引。"""
import sqlite3, os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DIR = r"D:\LegendOfMortal Wiki\data\portraits"
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

files = os.listdir(DIR)
idx = {}
for f in files:
    if not f.endswith(".png"):
        continue
    base = f[:-4]
    key, _, tex = base.partition("__")
    tex = tex.lower()
    # 纹理名 → 候选 id
    cands = [tex]
    for suf in ("_normal", "_normal2", "_angry1", "_angry2", "_laugh1", "_sad1",
                "_hurt", "_special1", "_special2"):
        if tex.endswith(suf):
            cands.append(tex[: -len(suf)])
    cands.append(key)
    score = 0 if "normal" in tex else 1
    for cand in cands:
        cur = idx.get(cand)
        if not cur or score < cur[0]:
            idx[cand] = (score, f)

ids = [r[0] for r in c.execute("select id from names")]
hit = [(i, idx[i][1]) for i in ids if i.lower() in idx]
print("命中", len(hit), "/", len(ids))
print("样例：", hit[:10])
miss = [i for i in ids if i.lower() not in idx][:20]
print("未命中：", miss)

# 名字维度兜底：用角色中文名再对一次（人名目录）
json.dump({k: v[1] for k, v in idx.items()},
          open(r"D:\LegendOfMortal Wiki\data\portrait_index.json", "w", encoding="utf-8"),
          ensure_ascii=False)
print("索引键", len(idx))
