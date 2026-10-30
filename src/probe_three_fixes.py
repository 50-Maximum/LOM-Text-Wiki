# -*- coding: utf-8 -*-
"""三处核对：①小竹的老虎大王甲 ②丹霞子识破佯攻的位置与立场 ③南宫深对婚约的表态。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=14):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:78] for x in r))

# ① 老虎大王甲
show("老虎大王甲 / 大王甲", """select script,seq,speaker,text from lines
    where text like '%老虎%甲%' or text like '%大王甲%' order by script,seq limit 12""")
show("郁竹 + 甲（穿戴/太重）", """select script,seq,speaker,text from lines
    where text like '%郁竹%' and text like '%甲%' order by script,seq limit 10""")

# ② 丹霞子 佯攻 / 外堡 / 西武林
show("丹霞子 + 佯攻", """select script,seq,speaker,text from lines
    where text like '%丹霞子%' and (text like '%佯攻%' or text like '%诈%' or text like '%识破%')
    order by script,seq limit 12""")
show("外堡 + 佯攻", """select script,seq,speaker,text from lines
    where text like '%外堡%' and text like '%佯攻%' order by script,seq limit 10""")
show("丹霞子 + 西武林", """select script,seq,speaker,text from lines
    where text like '%丹霞子%' and (text like '%西武林%' or text like '%武林盟%')
    order by script,seq limit 10""")

# ③ 南宫深 婚约
show("南宫深 + 婚约/退婚/取消", """select script,seq,speaker,text from lines
    where speaker='南宫深' and (text like '%婚%' or text like '%娶%' or text like '%嫁%')
    order by script,seq limit 14""")
show("提及上官萤婚约的旁人", """select script,seq,speaker,text from lines
    where text like '%婚约%' and (text like '%上官%' or text like '%南宫深%')
    order by script,seq limit 12""")
