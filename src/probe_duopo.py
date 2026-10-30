# -*- coding: utf-8 -*-
"""查「夺魄弟子急报惊变」这个事件的选项与条件。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

rows = list(c.execute("""select slug,name,lead,sections from pages
                         where type='事件' and name like '%夺魄%'"""))
for slug, name, lead, secs in rows:
    print("=" * 70)
    print(slug, "｜", name)
    print("lead:", (lead or "")[:160])
    S = json.loads(secs or "[]")
    for s in S:
        h = s.get("h")
        if h == "分支选项":
            print("\n-- 分支选项")
            for cr in (s.get("choice_rows") or []):
                print("   提问:", cr.get("prompt"))
                print("   场景:", cr.get("script"), " ", cr.get("scene"))
                for i, o in enumerate(cr.get("options") or [], 1):
                    print("     [%d] %s" % (i, o.get("text")))
                    print("         条件: %s" % (o.get("cond") or "（无）"))
                    print("         结果: %s" % (o.get("result") or "（无）"))
                    print("         跳转: %s %s" % (o.get("next") or "", o.get("next_title") or ""))
        elif h in ("剧情衔接",):
            print("\n-- 剧情衔接")
            for r in (s.get("rows") or []):
                print("   ", r.get("note"), "｜", r.get("script"), "｜", r.get("title"))
            for r in (s.get("branch_rows") or []):
                print("   分支:", r)
