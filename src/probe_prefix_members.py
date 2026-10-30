# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== 青城/崆峒/飞天/玄功 前缀成员")
for r in c.execute("""select name from pages where type='人物'
                      and (name like '青城·%' or name like '崆峒·%'
                           or name like '飞天门·%' or name like '玄功门·%'
                           or name like '锦香宫·%') order by name"""):
    print("   ", r[0])
print("\n=== 指定人物的 char_faction 原始记录")
for nm in ("高和子", "铁冠道人", "怀素真人", "不平道长", "停风子", "清虚子",
           "邹博", "姚知命", "孟仙谣", "郁城", "郁父", "郁母", "宝花", "郁宝花",
           "向无忧", "解无尘", "李富贵", "王二壮", "石公远", "福韫", "释明"):
    rows = c.execute("""select cf.faction, cf.score, cf.method from char_faction cf
                        join names n on n.id=cf.char_id where n.name=?""", (nm,)).fetchall()
    print("   %-6s %s" % (nm, rows or "—"))
