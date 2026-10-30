# -*- coding: utf-8 -*-
"""① 虎甲那场的场景标题与上下文 ② 丹霞子在唐门保卫战里的发言 ③ 丹霞子现有简介。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

print("=== ch8_2_6_4_break_start_01 上下文")
t = c.execute("select title from scenes where script='ch8_2_6_4_break_start_01'").fetchone()
print("  标题:", t[0] if t else "-")
for seq, sp, tx in c.execute("""select seq,speaker,text from lines
    where script='ch8_2_6_4_break_start_01' and seq between 90 and 110 order by seq"""):
    print("  %-4s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:80]))

print("\n=== 丹霞子 在 ch8_2_* 的发言")
for sc, seq, tx in c.execute("""select script,seq,text from lines where speaker='丹霞子'
    and script like 'ch8_2%' order by script,seq limit 16"""):
    print("  %-26s %-4s %s" % (sc, seq, (tx or "").replace("\n", " ")[:76]))

print("\n=== 丹霞子现有简介")
d = json.load(open(B + r"\intros_char.json", encoding="utf-8"))
v = d.get("人物/丹霞子") or {}
print("  %d 字 ｜ 脚注 %d" % (len(v.get("text") or ""), len(v.get("footnotes") or [])))
print(" ", (v.get("text") or "")[:400])
