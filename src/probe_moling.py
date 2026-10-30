# -*- coding: utf-8 -*-
"""唐默铃 考据材料：她自己的台词、招亲与逃婚的关键句。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

print("=== ch5_5_3 唐默铃的话")
for seq, tx in c.execute("""select seq,text from lines where script='ch5_5_3'
                            and speaker='唐默铃' order by seq limit 14"""):
    print("  %-4s %s" % (seq, (tx or "").replace("\n", " ")[:80]))

print("\n=== ch5_5_1 唐默铃的话")
for seq, tx in c.execute("""select seq,text from lines where script='ch5_5_1'
                            and speaker='唐默铃' order by seq limit 10"""):
    print("  %-4s %s" % (seq, (tx or "").replace("\n", " ")[:80]))

print("\n=== 招亲里她的关键句（ch5_2_7_1 / ch5_2_5）")
for sc in ("ch5_2_7_1", "ch5_2_5"):
    for seq, tx in c.execute("""select seq,text from lines where script=?
                                and speaker='唐默铃' order by seq limit 6""", (sc,)):
        print("  %-12s %-4s %s" % (sc, seq, (tx or "").replace("\n", " ")[:76]))

print("\n=== 她出场最多的场景")
for sc, n in c.execute("""select script,count(*) from lines where speaker='唐默铃'
                          group by script order by 2 desc limit 8"""):
    t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("  %-24s %3d ｜ %s" % (sc, n, (t[0] if t else "")[:24]))

pre = json.load(open(B + r"\chars_prefix.json", encoding="utf-8"))
tit = json.load(open(B + r"\chars_title.json", encoding="utf-8"))
print("\n前缀:", pre.get("唐默铃"), "｜ 称号:", tit.get("唐默铃"))
