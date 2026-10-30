# -*- coding: utf-8 -*-
"""核对唐惟元旧稿两处未经证实的说法：①「唐门被围时坐镇外堡，嘴上喊要溜，实际没走」"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== 唐惟元 + 外堡/后门/溜/逃")
for sc, seq, sp, tx in c.execute("""select script,seq,speaker,text from lines
    where speaker='唐惟元' and (text like '%外堡%' or text like '%后门%' or text like '%溜%'
      or text like '%逃%' or text like '%走人%' or text like '%撤%')
    order by script,seq limit 14"""):
    print("  %-22s %-4s %s" % (sc, seq, (tx or "").replace("\n", " ")[:76]))

print("\n=== 唐惟元 + 商队/生意/怕死")
for sc, seq, tx in c.execute("""select script,seq,text from lines
    where speaker='唐惟元' and (text like '%商队%' or text like '%我怕%' or text like '%胆小%')
    order by script,seq limit 10"""):
    print("  %-22s %-4s %s" % (sc, seq, (tx or "").replace("\n", " ")[:76]))
