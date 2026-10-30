# -*- coding: utf-8 -*-
"""查各感情线的结局段落 + 谁都没选时的收尾。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== endings 表里带 G11 的条件块 ==")
for cond, chain, n, seq, sample, text in c.execute(
        "select condition,chain,n,seq,sample,text from endings order by seq"):
    if "G11" in (chain or "") or "G11" in (cond or ""):
        sm = json.loads(sample or "[]")
        print(f"\n[{n}句 seq{seq}] {cond[:70]}")
        for s in sm[:3]:
            print("   ", s["speaker"], "：", s["text"][:100])

print("\n\n== ch8_8_1 里含「大师兄」「说相声」「光棍」「孤身」的段落 ==")
for seq, sp, tx, br in c.execute("""select seq,speaker,text,branch from lines
                                    where script='ch8_8_1' and (text like '%大师兄%'
                                    or text like '%说相声%' or text like '%光棍%'
                                    or text like '%孤身%') order by seq limit 40"""):
    print(f"  {seq:3} {sp}：{(tx or '')[:80]}")
    if br:
        print(f"       ← {br[:90]}")
