# -*- coding: utf-8 -*-
"""看几个人物现有简介的内容与脚注数，判断哪些需要重写。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = json.load(open(r"D:\LegendOfMortal Wiki\data\intros_char.json", encoding="utf-8"))
for n in ("唐惟元", "唐升", "唐布衣", "唐铮", "唐默铃"):
    v = d.get("人物/" + n) or {}
    t = v.get("text") or ""
    fns = v.get("footnotes") or []
    print("\n===== %s ｜ %d 字 ｜ 脚注 %d" % (n, len(t), len(fns)))
    print(t[:700] + ("…" if len(t) > 700 else ""))
