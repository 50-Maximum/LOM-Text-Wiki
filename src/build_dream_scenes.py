# -*- coding: utf-8 -*-
"""人工确认的梦境/幻境场景清单 → data/dream_scenes.json

判据：叙述框架明说这是梦（不是「我不是作梦吧」这类比喻）。
用户指出的一组：赵活的娘喊他回家吃饭、连着好几个选项——那是梦，S8500_01 系列。
"""
import io, sys, os, json, sqlite3

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db")).cursor()

ITEMS = [
    ("S8500_01", 23, "瑞杏", "你做梦了，赵君。"),
    ("S8500_01_01", 0, "", "（同属 S8500_01 梦境）"),
    ("S8500_01_02", 0, "", "（同属 S8500_01 梦境）"),
    ("S8500_01_03", 0, "", "（同属 S8500_01 梦境）"),
    ("S8500_01_04", 0, "", "（同属 S8500_01 梦境，梦醒前抱娃娃）"),
    ("ch1_2_4", 3, "？？？", "本宫来作你梦乡的守人。"),
    ("ch4_9_3_2", 2, "虞小梅", "美梦该醒了吗？毕竟是梦嘛。"),
    ("ch4_8_10_1", 2, "瑞杏", "……难得梦见本宫，怎能哭丧著脸呢？"),
    ("ch5_4_8_6", 1, "旁白", "令你昏昏沉沉，恋栈梦乡，舍不得醒。"),
    ("ch8_7_2_1", 1, "旁白", "那一晚你做了个梦，梦到孩提时，所以很早就醒了。"),
    ("S0208_04_01_07", 5, "？？？", "你料对了一半。 只是作梦而已，暂时。"),
    ("ch3_1_4_1", 7, "叶云舟", "不是你叫我们舞剑的吗？你何时睡着的。"),
]

out = {}
for sc, seq, sp, q in ITEMS:
    row = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    if not row:
        print("  跳过（场景不存在）", sc)
        continue
    out[sc] = {"title": row[0] or "", "seq": seq, "speaker": sp, "quote": q}

json.dump(out, open(os.path.join(B, "dream_scenes.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("写入梦境场景 %d 个" % len(out))
for sc, v in out.items():
    print("  %-18s %s ｜ %s" % (sc, (v["title"] or "")[:20], v["quote"][:40]))
