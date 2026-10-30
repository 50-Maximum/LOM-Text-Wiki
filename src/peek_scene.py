# -*- coding: utf-8 -*-
"""按需查某场景的笔记与原文上下文。用法: python peek_scene.py SCRIPT [seq] [radius]"""
import os, sys, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

script = sys.argv[1]
seq = int(sys.argv[2]) if len(sys.argv) > 2 else -1
rad = int(sys.argv[3]) if len(sys.argv) > 3 else 6

row = c.execute("select title,chapter,line_count from scenes where script=?", (script,)).fetchone()
print(f"== {script} 《{row[0] if row else '?'}》{row[1] if row else ''} {row[2] if row else 0} 句")

ns = c.execute("""select seq_from,seq_to,type,name,note,quote from notes
                  where script=? order by seq_from""", (script,)).fetchall()
if ns:
    print(f"-- 笔记 {len(ns)} 条")
    for r in ns:
        print(f"  [{r[0]:3}-{r[1]:3}] {r[2]:6} {r[3]}｜{r[4]}")
        print(f"       「{r[5]}」")
else:
    print("-- 尚无笔记")

if seq >= 0:
    print(f"-- 原文 seq {seq-rad}~{seq+rad}")
    for r in c.execute("select seq,speaker,text from lines where script=? and seq between ? and ? order by seq",
                       (script, seq - rad, seq + rad)):
        print(f"  {r[0]:3} {r[1]}：{(r[2] or '').replace(chr(10),' ')[:100]}")
