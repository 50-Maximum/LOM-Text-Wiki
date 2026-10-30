# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()
dream = set(json.load(open(B + r"\data\dream_scenes.json", encoding="utf-8")))

print("=== 含「因我心乱」的句子")
for sc, s, sp, t in c.execute("""select script,seq,speaker,text from lines
                                 where text like '%因我心乱%' or text like '%心乱，命丧%'"""):
    print(" ", sc, s, sp, "（梦）" if sc in dream else "（真）", (t or "")[:90])

print("\n=== ch8_7_2_2_1 前后（南溪相关）")
print(" 标题:", c.execute("select title,place from scenes where script='ch8_7_2_2_1'").fetchone())
for s, sp, t in c.execute("""select seq,speaker,text from lines where script='ch8_7_2_2_1'
                             and seq between 1 and 24 order by seq"""):
    print(" %4d %-8s %s" % (s, (sp or "")[:8], (t or "").replace("\n", " ")[:110]))

print("\n=== 南溪 出现的非梦场景（按脚本序）")
scs = [r[0] for r in c.execute("""select distinct script from lines where speaker='南溪'""")]
scs = [s for s in scs if s not in dream]
print(" %d 场：%s" % (len(scs), scs[:25]))
