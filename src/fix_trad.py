# -*- coding: utf-8 -*-
"""把 lines.text 与 notes.quote/note 里的繁体统一转简中，并重建 FTS。"""
import io, sys, sqlite3
from opencc import OpenCC
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CC = OpenCC("t2s")
db = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c = db.cursor()

print("=== schema ===")
for name in ("lines", "notes"):
    print(name, [r[1] for r in c.execute("pragma table_info(%s)" % name)])
for nm, sql in c.execute("select name,sql from sqlite_master where name like '%fts%'"):
    print(nm, "->", (sql or "")[:200])

# lines
rows = c.execute("select id,text,uni from lines").fetchall()
upd = []
for sid, tx, uni in rows:
    a = CC.convert(tx or "")
    b = CC.convert(uni or "")
    if a != (tx or "") or b != (uni or ""):
        upd.append((a, b, sid))
c.executemany("update lines set text=?, uni=? where id=?", upd)
n1 = len(upd)
print("\nlines 转换 %d 行" % n1)

# notes
n2 = 0
cols = [r[1] for r in c.execute("pragma table_info(notes)")]
nu = []
for rid, q, nt in c.execute("select rowid,quote,note from notes").fetchall():
    a, b = CC.convert(q or ""), CC.convert(nt or "")
    if a != (q or "") or b != (nt or ""):
        nu.append((a, b, rid))
c.executemany("update notes set quote=?, note=? where rowid=?", nu)
n2 = len(nu)
print("notes 转换 %d 行（列 %s）" % (n2, cols))
db.commit()

# FTS 重建
try:
    c.execute("insert into lines_fts(lines_fts) values('rebuild')")
    print("FTS rebuild 完成")
except Exception as e:
    print("rebuild 失败：", e)
    try:
        c.execute("delete from lines_fts")
        c.execute("insert into lines_fts(rowid, uni) select id, uni from lines")
        print("FTS 重灌完成")
    except Exception as e2:
        print("重灌失败：", e2)
db.commit()
print("剩余繁体台词：", sum(1 for (tx,) in c.execute("select text from lines")
                       if tx and CC.convert(tx) != tx))
