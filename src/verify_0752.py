# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== 杏花林成员 ==")
r = c.execute("select infobox,sections from pages where type='势力' and name='杏花林'").fetchone()
inf = json.loads(r["infobox"] or "{}") if r else {}
print("  成员数", inf.get("成员", "-"))
if r:
    for s in json.loads(r["sections"] or "[]"):
        if (s.get("h") or "").startswith("本派成员"):
            for rw in (s.get("rows") or []):
                print("    ·", rw.get("note", "")[:40])
print("\n== 关键人物页 ==")
for nm in ["唐门·唐皮康", "唐门·唐许亚霆", "杏花林·瑞笙", "杏花林·万里鹏程",
           "崆峒派·夏侯兰", "火炎山剑阁·全胜利", "江湖·叶辰"]:
    x = c.execute("select name,title,substr(lead,1,54) as ld from pages where type='人物' and name=?", (nm,)).fetchone()
    print("  %-20s %s" % (nm, ((x["title"] or "") + " | " + (x["ld"] or "")) if x else "无页"))
print("\n人物页", c.execute("select count(*) from pages where type='人物'").fetchone()[0])
