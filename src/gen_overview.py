# -*- coding: utf-8 -*-
"""生成总览：章节、人物、门派、分支统计。纯文本，无装饰符号。"""
import os, sqlite3, collections, shutil

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
OUT = r"D:\LegendOfMortal Wiki\data\summary"
os.makedirs(OUT, exist_ok=True)
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row

def q(sql, a=()):
    return c.execute(sql, a).fetchall()

L = []
L.append("活侠传 文本总览")
L.append("生成时间 " + __import__("time").strftime("%Y-%m-%d %H:%M"))
L.append("")
L.append("一、总体规模")
tot = q("SELECT COUNT(*) n FROM lines")[0]["n"]
sc = q("SELECT COUNT(*) n FROM scenes WHERE line_count>0")[0]["n"]
sp = q("SELECT COUNT(DISTINCT speaker) n FROM lines")[0]["n"]
ch = q("SELECT COUNT(*) n FROM choices")[0]["n"]
fl = q("SELECT COUNT(*) n FROM flags")[0]["n"]
L.append("台词 %d 条，场景 %d 个，说话人 %d 位，分支判定 %d 组，旗标改动 %d 次。" % (tot, sc, sp, ch, fl))
L.append("")

L.append("二、章节结构")
for r in q("SELECT chapter, COUNT(*) n, SUM(line_count) l FROM scenes WHERE line_count>0 GROUP BY chapter ORDER BY chapter"):
    L.append("%s：场景 %d 个，台词 %d 条。" % (r["chapter"], r["n"], r["l"]))
L.append("")

L.append("三、出场最多的人物")
for r in q("SELECT speaker, COUNT(*) n FROM lines WHERE speaker<>'旁白' GROUP BY speaker ORDER BY n DESC LIMIT 30"):
    L.append("%s：%d 句。" % (r["speaker"], r["n"]))
L.append("")

L.append("四、门派与势力（根据旗标好感度条目）")
seen = set()
for r in q("SELECT flag,label FROM flaginfo WHERE label LIKE '%好感度%' OR label LIKE '%门派%' ORDER BY label"):
    lab = r["label"].replace("好感度", "").strip()
    if lab and lab not in seen:
        seen.add(lab)
        L.append("%s（%s）" % (lab, r["flag"]))
L.append("")

L.append("五、词条来源")
for r in q("SELECT ns, COUNT(*) n FROM entries GROUP BY ns ORDER BY n DESC"):
    L.append("%s：%d 条。" % (r["ns"], r["n"]))
L.append("")

L.append("六、分支最多的场景")
for r in q("""SELECT script, COUNT(*) n FROM choices GROUP BY script ORDER BY n DESC LIMIT 10"""):
    L.append("%s：%d 组判定。" % (r["script"], r["n"]))

txt = "\n".join(L)
p = os.path.join(OUT, "00-总览.txt")
open(p, "w", encoding="utf-8").write(txt)
desk = os.path.join(os.path.expanduser("~"), "Desktop", "活侠传-文本总览.txt")
shutil.copyfile(p, desk)
print(txt[:1500])
print("saved", p)
