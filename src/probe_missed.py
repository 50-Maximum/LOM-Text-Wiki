# -*- coding: utf-8 -*-
"""别名审计引出的两处补漏：
① 唐布衣 卧云岗败于石公远、卧榻伤重（ch4_6_7_break_start_01 / ch4_6_6）
② 唐默铃 逃婚（ch5_5_3）、媒人（ch5_2_5）
"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def dump(label, script, kw=(), lim=26):
    print("\n=== %s ｜ %s" % (label, script))
    for seq, sp, tx in c.execute("""select seq,speaker,text from lines
                                    where script=? order by seq limit 200""", (script,)):
        t = (tx or "").replace("\n", " ")
        if kw and not any(k in t for k in kw):
            continue
        print("  %-4s %-8s %s" % (seq, (sp or "")[:8], t[:84]))
        lim -= 1
        if lim <= 0:
            break

dump("大师兄败于飞石帮主", "ch4_6_7_break_start_01", ("大师兄", "石", "伤", "败", "输", "血"))
dump("大师兄卧榻伤重垂危", "ch4_6_6", ("大师兄", "伤", "脉", "命", "救"))
dump("小师妹逃婚夜寻赵活", "ch5_5_3", ("逃", "婚", "小师妹", "嫁"))
dump("带媒人的数量", "ch5_2_5", ("媒", "嫁", "招亲", "提亲"))
