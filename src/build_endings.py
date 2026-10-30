# -*- coding: utf-8 -*-
"""抽终章 epilogue 的条件块，写 data/endings.json + 库表 endings。

《活侠传》没有独立结局场景：终章 ch8_8_1《小竹的愿望》用 if/else 把
几十段尾声按旗标拼起来，条件不同则结局不同。
"""
import os, sys, io, sqlite3, json, collections, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.execute("PRAGMA journal_mode=WAL")

FINAL = "ch8_8_1"

rows = c.execute("""select seq,speaker,text,branch from lines where script=?
                    order by seq""", (FINAL,)).fetchall()
groups = collections.OrderedDict()
for seq, sp, tx, br in rows:
    groups.setdefault(br or "（无条件）", []).append(
        {"seq": seq, "speaker": sp, "text": (tx or "").replace("\n", " ")})

out = []
for cond, arr in groups.items():
    # 条件链拆开，取最末一条作为这段的判定
    parts = [p for p in cond.split(" > ") if p]
    out.append({
        "condition": parts[-1] if parts else "（无条件）",
        "chain": parts,
        "n": len(arr),
        "first_seq": arr[0]["seq"],
        "sample": arr[:3],
        "text": "".join(x["text"] for x in arr),
    })

json.dump(out, open(os.path.join(BASE, "data", "endings.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

c.executescript("""drop table if exists endings;
create table endings(script TEXT, condition TEXT, chain TEXT, n INT, seq INT,
                     sample TEXT, text TEXT);""")
c.executemany("insert into endings values(?,?,?,?,?,?,?)",
              [(FINAL, e["condition"], json.dumps(e["chain"], ensure_ascii=False),
                e["n"], e["first_seq"], json.dumps(e["sample"], ensure_ascii=False),
                e["text"]) for e in out])
c.commit()

print("条件块", len(out), "总句数", sum(e["n"] for e in out))
print("\n== 条件块一览（句数 >= 3）==")
for e in out:
    if e["n"] < 3:
        continue
    print(f"  [{e['n']:3}句 seq{e['first_seq']:3}] {e['condition'][:60]}")
    print(f"      {e['sample'][0]['text'][:76]}")
