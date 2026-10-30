# -*- coding: utf-8 -*-
"""找「初识唐铮」：年表选项「你是来找工作的吗？」/「你是来找死的吗？」未进 choices 表，
改从 lines 里搜关键词，并按最早出现的唐铮场景排序。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
c2 = json.load(open(B + r"\scene_next.json", encoding="utf-8"))
order = json.load(open(B + r"\scene_order.json", encoding="utf-8")) \
    if __import__("os").path.exists(B + r"\scene_order.json") else {}
titles = dict(c.execute("select script,title from scenes"))

for kw in ("找工作", "找死", "打杂", "应征"):
    print("\n=== 台词命中「%s」" % kw)
    for sc, seq, sp, tx in c.execute(
            """select script,seq,speaker,text from lines where text like ?
               order by script,seq limit 6""", ("%" + kw + "%",)):
        print("   %-26s %-4s %-8s %s" % (sc, seq, (sp or "")[:8],
                                         (tx or "").replace("\n", " ")[:56]))

print("\n=== 唐铮作为说话人最早出现的场景")
cnt = {}
for sc, n in c.execute("""select script,count(*) from lines
                          where speaker='唐铮' group by script"""):
    cnt[sc] = n
for sc, n in sorted(cnt.items(), key=lambda x: -x[1])[:12]:
    print("   %-26s %3d 句   %s" % (sc, n, (titles.get(sc) or "")[:30]))
