# -*- coding: utf-8 -*-
"""多重身份排查：无相祖师 / 无念僧 / 铁冠道人 / 千面人魔 / 画中仙 / 释明。
先把每个名字的出场场景与「揭示句」都摊开，再谈并页。
"""
import io, sys, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

NAMES = ["无相祖师", "无念僧", "铁冠道人", "铁冠道长", "千面人魔", "画中仙", "释明", "老和尚"]
print("=== 各名字出现次数与场景数")
for n in NAMES:
    tot = c.execute("select count(*) from lines where text like ?", ("%" + n + "%",)).fetchone()[0]
    scs = c.execute("select count(distinct script) from lines where text like ?", ("%" + n + "%",)).fetchone()[0]
    print("  %-6s 台词 %4d 句 ｜ 场景 %3d 个" % (n, tot, scs))

def reveal(label, a, b):
    print("\n=== %s 与 %s 同句" % (a, b))
    rows = list(c.execute("""select script,seq,speaker,text from lines
        where text like ? and text like ? order by script,seq limit 12""",
        ("%" + a + "%", "%" + b + "%")))
    if not rows:
        print("  （无）")
    for sc, seq, sp, tx in rows:
        print("  %-26s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:78]))

reveal("无相祖师/铁冠", "无相祖师", "铁冠")
reveal("无相祖师/无念僧", "无相祖师", "无念僧")
reveal("无念僧/铁冠", "无念僧", "铁冠")
reveal("千面人魔/画中仙", "千面人魔", "画中仙")
reveal("千面人魔/铁冠", "千面人魔", "铁冠")
reveal("释明/千面", "释明", "千面")
reveal("老和尚/千面", "老和尚", "千面")
