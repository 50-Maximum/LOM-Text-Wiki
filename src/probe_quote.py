# -*- coding: utf-8 -*-
"""查「我要杀了你」现在挂在哪些页面的哪条笔记上，确认不再错配。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== notes 里含该引文的 ==")
for r in c.execute("""select script,seq_from,seq_to,type,name,note,quote from notes
                      where quote like '%我要杀了你%'"""):
    print("  ", r)

print("\n== 该句在原文里的位置 ==")
for r in c.execute("""select script,seq,speaker,substr(text,1,60) from lines
                      where text like '%我要杀了你%' limit 10"""):
    print("  ", r)

print("\n== 页面 sections 里含该引文的 ==")
n = 0
for slug, secs in c.execute("select slug,sections from pages where type in ('人物','事件','势力','地点')"):
    if "我要杀了你" in (secs or ""):
        n += 1
        print("  ", slug)
        if n > 10:
            break
print("  共", n)
