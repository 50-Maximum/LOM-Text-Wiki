# -*- coding: utf-8 -*-
import sqlite3, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
OUT = r"D:\LegendOfMortal Wiki\data\dossier_char"
names = sys.argv[1:] or ["唐衫", "李富贵", "画中仙"]
for name in names:
    L = [f"===== {name} ====="]
    notes = c.execute("""select script,seq_from,note,quote from notes
                         where type='人物' and name=? order by script,seq_from""", (name,)).fetchall()
    L.append(f"-- 笔记 {len(notes)} 条（前 35）--")
    for sc, a, note, q in notes[:35]:
        L.append(f"{sc}#{a} {note} | {q}")
    gs = c.execute("""select year,month,xun,name,substr(body,1,240) from guide_events
                      where body like ? order by year,month limit 5""", (f"%{name}%",)).fetchall()
    if gs:
        L.append("-- 攻略 --")
        for y, mo, x, ev, body in gs:
            L.append(f"[{y}年{mo}月{x or ''}] {ev}: {body.replace(chr(10),' ')[:220]}")
    txt = "\n".join(L)
    open(os.path.join(OUT, name + ".txt"), "w", encoding="utf-8").write(txt)
    print("导出", name, len(txt))
