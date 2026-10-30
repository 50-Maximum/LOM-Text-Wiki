# -*- coding: utf-8 -*-
"""校验 factions_fix.json / intros_char.json 里所有引文是否逐字存在于 lines 表。"""
import sqlite3, io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
norm = lambda s: re.sub(r"\s+", "", s or "")

def check(path, keyname):
    d = json.load(open(path, encoding="utf-8"))
    if keyname:
        d = d.get(keyname) or {}
    bad = 0
    for slug, v in d.items():
        fns = v.get("footnotes") or []
        srcs = v.get("sources") or []
        items = []
        for fn in fns:
            items.append((fn.get("n", "?"), fn.get("script"), fn.get("quote")))
        for s in srcs:
            items.append(("s", s.get("script"), s.get("quote")))
        for n, sc, q in items:
            if not sc:
                print(f"[{slug}] 脚注{n}: 缺 script"); bad += 1; continue
            if not q:
                print(f"[{slug}] 脚注{n}: 缺 quote"); bad += 1; continue
            rows = c.execute("select seq from lines where script=?", (sc,)).fetchall()
            if not rows:
                print(f"[{slug}] 脚注{n}: 场景 {sc} 不存在"); bad += 1; continue
            # 逐字匹配（去空白）
            hit = False
            for (seq,) in c.execute("select seq from lines where script=? and replace(replace(replace(text,char(10),''),char(13),''),' ','') like ?", (sc, f"%{norm(q)}%")):
                hit = True
                break
            if not hit:
                print(f"[{slug}] 脚注{n}: {sc} 引文未命中 → {q[:36]}")
                bad += 1
    print(f"{path}: {bad} 条未命中")
    return bad

check(r"D:\LegendOfMortal Wiki\data\factions_fix.json", "intro")
check(r"D:\LegendOfMortal Wiki\data\intros_char.json", "")
check(r"D:\LegendOfMortal Wiki\data\intros_world.json", "")
