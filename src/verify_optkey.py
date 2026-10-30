# -*- coding: utf-8 -*-
"""验：南宫远就任武林盟主 的触发条件、以及 talk 菜单选项条件是否落地。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

for slug in ("事件/南宫远就任武林盟主", "场景/ch6_6_2_break_start_01"):
    r = c.execute("select lead,sections from pages where slug=?", (slug,)).fetchone()
    print("=" * 70)
    print(slug)
    if not r:
        print("  无此页")
        continue
    for s in json.loads(r[1] or "[]"):
        if s.get("h") not in ("触发条件", "分支选项"):
            continue
        print(" --", s.get("h"))
        for x in (s.get("rows") or [])[:6]:
            print("    ", (x.get("note") or "")[:150], "|", x.get("script") or "")
        for b in (s.get("choice_rows") or []):
            print("    提问:", (b.get("prompt") or "")[:30], "free=", b.get("free"), "脚本", b.get("script"))
            for o in (b.get("options") or [])[:12]:
                print("      %-14s 条件：%-40s 结果：%s" %
                      (o.get("text"), (o.get("cond") or "无")[:40], (o.get("result") or "")[:46]))
