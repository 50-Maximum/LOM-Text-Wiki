# -*- coding: utf-8 -*-
"""给南溪找一条非梦境的、能支撑「背叛武林盟」的原文。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
dream = set(json.load(open(r"D:\LegendOfMortal Wiki\data\dream_scenes.json", encoding="utf-8")))
rows = c.execute("""select script,seq,text from lines
                    where speaker='南溪' and (text like '%武林盟%' or text like '%背叛%')
                    order by script,seq""").fetchall()
print("命中 %d 条" % len(rows))
for sc, seq, tx in rows:
    flag = "（梦）" if sc in dream else ""
    print(" %-18s %4d %s %s" % (sc, seq, flag, (tx or "").replace("\n", " ")[:110]))
