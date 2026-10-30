# -*- coding: utf-8 -*-
"""给每个场景生成事件名：官方名 > 规则名（地点+工作/自由/闲聊） > 首句推导 > 待确认。"""
import sqlite3, re, os, collections, shutil

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row

cols = [r[1] for r in c.execute("PRAGMA table_info(scenes)")]
if "title" not in cols:
    c.execute("ALTER TABLE scenes ADD COLUMN title TEXT")
if "title_src" not in cols:
    c.execute("ALTER TABLE scenes ADD COLUMN title_src TEXT")

MANUAL = {
    "ch6_7_1": "南宫远就任武林盟主",
}

KIND = {"work": "工作", "free": "自由行动", "talk": "闲聊"}


def first_lines(script, n=2):
    rows = c.execute("SELECT speaker,text FROM lines WHERE script=? AND text<>'' ORDER BY seq LIMIT ?",
                     (script, n)).fetchall()
    return [(r["speaker"], r["text"]) for r in rows]


def clean(s):
    s = re.sub(r"[\r\n]+", " ", s or "").strip()
    s = re.sub(r"^[……\.。？！?！、，,\s]+", "", s)
    return s


GENERIC = ("嗯", "啊", "哦", "唔", "什么", "怎么", "为何", "这是", "那个人", "是谁")

scenes = c.execute("SELECT script,chapter,place,line_count FROM scenes WHERE line_count>0").fetchall()
official = {}
for r in c.execute("""SELECT ch.script, k.title FROM choices ch JOIN chk k ON k.id=ch.checkpoint
                      WHERE ch.checkpoint<>'' AND k.title IS NOT NULL GROUP BY ch.script"""):
    official.setdefault(r["script"], r["title"])

stat = collections.Counter()
weak = []
for s in scenes:
    sc, place = s["script"], s["place"] or ""
    if sc in MANUAL:
        title, src = MANUAL[sc], "manual"
    elif sc in official:
        title, src = official[sc], "official"
    else:
        m = re.match(r"^(.+?)_(work|free|talk)_(\d+)$", sc)
        if m and place:
            title, src = "%s・%s（%s）" % (place, KIND[m.group(2)], m.group(3)), "rule"
        else:
            fl = first_lines(sc)
            if not fl:
                title, src = (place + "・剧情" if place else ""), "weak"
                weak.append((sc, s["chapter"], place, "", s["line_count"]))
            else:
                t = clean(fl[0][1])
                t = re.split(r"[。！？\n]", t)[0].strip()
                if len(t) > 16:
                    t = t[:16] + "…"
                if len(t) < 6 or t.startswith(GENERIC):
                    title, src = ((place + "・" + t) if place else t), "weak"
                    weak.append((sc, s["chapter"], place, t, s["line_count"]))
                else:
                    title, src = t, "derived"
    stat[src] += 1
    c.execute("UPDATE scenes SET title=?, title_src=? WHERE script=?", (title, src, sc))
c.commit()

print("统计:", dict(stat), "弱名:", len(weak))
out = os.path.join(r"D:\LegendOfMortal Wiki\data\summary", "待确认事件.txt")
os.makedirs(os.path.dirname(out), exist_ok=True)
lines = ["待人工确认的事件（自动命名不可靠）", "共 %d 条" % len(weak), ""]
for sc, ch, pl, t, n in sorted(weak, key=lambda x: -x[4]):
    lines.append("%s | %s | %s | %s | %d 句" % (sc, ch, pl or "-", t or "-", n))
open(out, "w", encoding="utf-8").write("\n".join(lines))
shutil.copyfile(out, os.path.join(os.path.expanduser("~"), "Desktop", "活侠传-待确认事件.txt"))
print("导出:", out)
