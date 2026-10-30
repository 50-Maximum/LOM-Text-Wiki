# -*- coding: utf-8 -*-
"""用年表行里的「选项原文」当指纹，去 lines 表里反查剧本。"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
db = sqlite3.connect(B + r"\wiki.db")
c = db.cursor()
print("lines 列:", [r[1] for r in c.execute("pragma table_info(lines)")])

# 年表 8 行的关键选项指纹
PROBES = {
    "你，听过唐门吗？/初识唐升": ["附和三师兄", "讲点干话刺激他", "讲点好听的话安慰他"],
    "招募弟子结果": ["不单没招到人", "还被飞石帮的人打了一顿抢走零用钱"],
    "照镜子": ["还不算差", "内在更重要", "实在是难看"],
    "惊吓指数": ["好言相劝", "讲干话对付他"],
    "初识唐布衣": ["人家只不过穿体面点", "我好像懂"],
    "初识唐铮": ["你是来找工作的吗", "你是来找死的吗"],
    "四书事件(一)同门霸凌": ["好汉不吃眼前亏", "老子跟你们拼了"],
    "四书事件(二)蒙面人前辈": ["晚辈非得亲手了断", "稍微试试再告状也不迟"],
}
for label, ps in PROBES.items():
    print("\n=== " + label)
    for p in ps:
        rows = list(c.execute(
            """select script,seq,text,speaker from lines
               where text like ? order by script,seq limit 4""", ("%" + p + "%",)))
        if not rows:
            rows = list(c.execute(
                """select script,seq,text,speaker from lines
                   where uni like ? order by script,seq limit 4""", ("%" + p + "%",)))
        if rows:
            for sc, seq, ch, sp in rows:
                print("   OK  %-26s seq%-5s %s" % (sc, seq, (ch or "")[:60]))
        else:
            print("   --  %s  未命中" % p)
