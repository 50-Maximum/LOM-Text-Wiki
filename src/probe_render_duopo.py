# -*- coding: utf-8 -*-
"""看场景页与事件页到底渲染出什么（sections 原样打印）。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

for slug in ("场景/ch5_6_5_3", "事件/夺魄弟子急报金乌夺功"):
    r = c.execute("select slug,name,lead,sections from pages where slug=?", (slug,)).fetchone()
    print("=" * 72)
    if not r:
        print("无此页:", slug)
        continue
    print(r[0], "｜", r[1])
    print("lead:", r[2])
    for s in json.loads(r[3] or "[]"):
        h = s.get("h") or list(s.keys())[0]
        print("\n-- 段:", h)
        for k, v in s.items():
            if k == "h":
                continue
            if k == "choice_rows":
                for cr in v:
                    print("   提问:", cr.get("prompt"))
                    for i, o in enumerate(cr.get("options") or [], 1):
                        print("     [%d] %s ｜ 条件=%s ｜ 跳=%s" %
                              (i, o.get("text"), o.get("cond") or "无", o.get("next") or ""))
            elif isinstance(v, list):
                for x in v[:14]:
                    print("   ", json.dumps(x, ensure_ascii=False)[:180])
                if len(v) > 14:
                    print("    ... 共 %d 条" % len(v))
            else:
                print("   ", str(v)[:300])
