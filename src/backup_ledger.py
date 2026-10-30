# -*- coding: utf-8 -*-
"""备份 / 恢复 ledger 与 entities（重建库时用）。"""
import sqlite3, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
BAK = r"D:\LegendOfMortal Wiki\data\ledger_backup.json"
mode = sys.argv[1] if len(sys.argv) > 1 else "save"

if mode == "save":
    c = sqlite3.connect(DB)
    out = {}
    for t in ("ledger", "entities"):
        cols = [r[1] for r in c.execute(f"pragma table_info({t})")]
        rows = c.execute(f"select * from {t}").fetchall()
        out[t] = {"cols": cols, "rows": rows}
        print(t, len(rows), "行", cols)
    json.dump(out, open(BAK, "w", encoding="utf-8"), ensure_ascii=False)
    print("备份写入", BAK, round(os.path.getsize(BAK) / 1048576, 1), "MB")
else:
    data = json.load(open(BAK, encoding="utf-8"))
    c = sqlite3.connect(DB)
    c.execute("PRAGMA journal_mode=WAL")
    for t in ("ledger", "entities"):
        cols = data[t]["cols"]
        c.execute(f"drop table if exists {t}")
        c.execute(f"create table {t}({', '.join(cols)})")
        ph = ",".join("?" * len(cols))
        c.executemany(f"insert into {t} values({ph})", data[t]["rows"])
        print(t, "恢复", len(data[t]["rows"]), "行")
    c.commit()
    print("完成")
