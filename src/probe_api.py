# -*- coding: utf-8 -*-
"""核对场景页的分支段 + 前端页面是否可访问。"""
import urllib.request, urllib.parse, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def get(u):
    return json.load(urllib.request.urlopen("http://127.0.0.1:8765" + u, timeout=20))

d = get("/api/page?slug=" + urllib.parse.quote("场景/S0017_01"))
print("场景页:", d["name"], "sections:", [s["h"] for s in d["sections"]])
for s in d["sections"]:
    if s["h"] == "分支与后果":
        print("  分支条数:", len(s["choices"]))
        for c in s["choices"][:6]:
            print(f"    [{c['kind']}#{c['idx']}] {c['text'][:20]} cond={c['cond']} flags={c['flags']} scenes={c['scenes']}")

d2 = get("/api/page?slug=" + urllib.parse.quote("路线/叶云裳"))
print("\n路线页:", d2["name"], "sections:", [s["h"] for s in d2["sections"]])
print("  infobox:", d2["infobox"])
print("  第一段:", d2["lead"][:80])

d3 = get("/api/page?slug=" + urllib.parse.quote("结局/终章"))
print("\n结局页:", d3["name"], "sections:", [(s["h"], len(s.get("rows") or [])) for s in d3["sections"]])

html = urllib.request.urlopen("http://127.0.0.1:8765/wiki", timeout=20).read().decode("utf-8")
print("\n/wiki 长度", len(html), "含 rows 渲染:", "s.rows" in html, "含 choices:", "s.choices" in html)
