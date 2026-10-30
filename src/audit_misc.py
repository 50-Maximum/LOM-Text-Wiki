# -*- coding: utf-8 -*-
"""批次审：①南溪脚注2 复核 ②各类型导语/脚注/链接缺口 ③有选项却没显示选项的页面。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

print("=== ① 南溪脚注")
r = c.execute("select slug,lead,sections from pages where name='南溪' or slug like '%南溪%'").fetchall()
for slug, lead, secs in r:
    print(" 页", slug)
    for s in json.loads(secs or "[]"):
        if s.get("h") in ("脚注", "简介"):
            for x in (s.get("rows") or [])[:8]:
                print("   ", x.get("note", "")[:120], "|", x.get("script"), "seq", x.get("seq"))
            if s.get("html"):
                print("    html:", s["html"][:200])

print("\n=== ② 各类型缺口")
types = [x[0] for x in c.execute("select distinct type from pages order by type")]
for t in types:
    n = c.execute("select count(*) from pages where type=? and hidden=0", (t,)).fetchone()[0]
    nol = c.execute("""select count(*) from pages where type=? and hidden=0
                       and (lead is null or length(lead)<12)""", (t,)).fetchone()[0]
    nofoot = c.execute("""select count(*) from pages where type=? and hidden=0
                          and sections not like '%脚注%'""", (t,)).fetchone()[0]
    print("  %-8s %5d 页 ｜ 导语<12字 %4d ｜ 无脚注 %4d" % (t, n, nol, nofoot))

print("\n=== ③ 有选项的剧本，页面里没显示分支选项")
cb = json.load(open(B + r"\data\choice_branch.json", encoding="utf-8"))
miss = []
for sc in cb:
    row = c.execute("select type,slug,sections from pages where slug in (?,?)",
                    ("场景/" + sc, "事件/" + sc)).fetchall()
    if not row:
        r2 = c.execute("select type,slug,sections from pages where slug='场景/'||?", (sc,)).fetchone()
        if not r2:
            miss.append((sc, "无页面"))
            continue
        row = [r2]
    ok = any("choice_rows" in (s or "") for _, _, s in row)
    if not ok:
        miss.append((sc, "有选项块未显示"))
print("  缺失 %d 个：%s" % (len(miss), miss[:12]))
