# -*- coding: utf-8 -*-
"""①参考 wiki 关于练功塔的原文 ②页面里把「第三关楼主」写在什么位置 ③练功塔相关页面清单"""
import io, sys, os, re, json, sqlite3, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REF = r"C:\Users\Luo\Downloads\LoM-wiki-1.7.0\LoM-wiki-1.7.0"
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

for rel in (r"docs\event\badends\index.md", r"docs\other\qna\202411.md",
            r"docs\other\news\20240607-01-demoUpdate.md", r"docs\people\factions\tang-men.md"):
    p = os.path.join(REF, rel)
    if not os.path.exists(p):
        continue
    s = open(p, encoding="utf-8", errors="replace").read()
    print("=" * 70, rel)
    for m in re.finditer(r"[^\n]*(练功塔|練功塔)[^\n]*", s):
        a = max(0, m.start() - 260)
        print("\n…", s[a:m.end() + 260].replace("\n", "\n  "))
        break

print("\n" + "=" * 70, "页面：赵活 intro 里提到第三关/练功塔的句子")
lead = c.execute("select lead from pages where slug='人物/赵活'").fetchone()[0]
for m in re.finditer(r"[^。]*?(练功塔|第三关|楼主)[^。]*。", lead or ""):
    print("  -", m.group(0).strip())

print("\n=== 相关页面")
for slug in ("地点/唐门-练功塔", "设施/练功塔", "事件/各派弟子闯练功塔",
             "事件/赵活闯练功塔第三关", "事件/赵活守塔痛打师弟", "事件/赵活弃权第三关"):
    r = c.execute("select type,name,lead,infobox from pages where slug=?", (slug,)).fetchone()
    print("\n", slug, "|", r[1] if r else "（无）")
    if r:
        print("   lead:", (r[2] or "")[:160])
        print("   infobox:", (r[3] or "")[:160])
