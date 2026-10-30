# -*- coding: utf-8 -*-
"""对比新旧库的表与行数，决定要从备份里补哪些表。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
NEW = r"D:\LegendOfMortal Wiki\data\wiki.db"
OLD = r"D:\LegendOfMortal Wiki\data\wiki.db.bak_before_6001"


def tables(p):
    c = sqlite3.connect(p)
    t = [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
    cnt = {}
    for x in t:
        try:
            cnt[x] = c.execute('select count(*) from "%s"' % x).fetchone()[0]
        except Exception:
            cnt[x] = -1
    c.close()
    return cnt


a = tables(NEW)
b = tables(OLD)
print("%-16s %8s %8s" % ("表", "新库", "备份"))
for k in sorted(set(a) | set(b)):
    print("%-16s %8s %8s" % (k, a.get(k, "-"), b.get(k, "-")))
print("\n仅备份有:", [k for k in b if k not in a])
