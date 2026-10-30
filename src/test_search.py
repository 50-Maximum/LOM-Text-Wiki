# -*- coding: utf-8 -*-
"""测搜索：脚本号、整句、短语能不能查到。"""
import io, json, sys, urllib.parse, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def s(q):
    u = "http://127.0.0.1:8765/api/search2?q=" + urllib.parse.quote(q)
    return json.loads(urllib.request.urlopen(u, timeout=20).read().decode("utf-8"))


for query in ("ch3_5_3_7_1", "撤退到邻镇", "偏僻小镇", "S9904_01", "绕远路到这偏僻小镇"):
    d = s(query)
    print("=== %s" % query)
    print("   pages %d | scenes %d | lines %d" % (len(d.get("pages") or []),
                                                  len(d.get("scenes") or []),
                                                  len(d.get("lines") or [])))
    for p in (d.get("pages") or [])[:3]:
        print("   page:", p.get("slug"))
    for sc in (d.get("scenes") or [])[:3]:
        print("   scene:", sc.get("script"), sc.get("title"))
    for ln in (d.get("lines") or [])[:3]:
        print("   line:", ln.get("script"), ln.get("seq"), (ln.get("text") or "")[:40])
