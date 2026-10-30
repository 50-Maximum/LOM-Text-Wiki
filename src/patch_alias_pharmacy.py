# -*- coding: utf-8 -*-
"""补别名：唐门医馆／唐门药铺 都指 地点/唐门-药铺。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()
anchor = '_al += [(a, f"地点/{t}") for a, t in PMERGE.items()]'
assert anchor in s, "别名块未找到"
if "唐门医馆" not in s:
    s = s.replace(anchor, anchor + '\n'
                  '_al += [("唐门医馆", "地点/唐门-药铺"), ("唐门药铺", "地点/唐门-药铺")]', 1)
    open(S, "w", encoding="utf-8").write(s)
    print("build_wiki2：已加 唐门医馆／唐门药铺 别名")
else:
    print("已存在别名，跳过")
