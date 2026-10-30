# -*- coding: utf-8 -*-
"""收尾自检：接口、搜索、路线列表、页面数。"""
import urllib.request, urllib.parse, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = "http://127.0.0.1:8765"

def get(p):
    return json.load(urllib.request.urlopen(B + p, timeout=20))

print("首页", len(urllib.request.urlopen(B + "/", timeout=20).read()), "字节")

d = get("/api/pages?type=" + urllib.parse.quote("路线") + "&limit=20")
print("路线列表:", d["total"], [r["name"] for r in d["rows"]])

d = get("/api/pages?type=" + urllib.parse.quote("结局"))
print("结局列表:", d["total"], [r["name"] for r in d["rows"]])

s = get("/api/search2?q=" + urllib.parse.quote("无常针"))
print("搜索「无常针」:", len(s.get("pages", [])), "页", len(s.get("lines", [])), "句")
for p in (s.get("pages") or [])[:5]:
    print("   ", p.get("slug"), p.get("name"))

for slug in ("场景/ch5_3_1", "路线/上官萤", "结局/终章", "人物/虞小梅"):
    d = get("/api/page?slug=" + urllib.parse.quote(slug))
    print(slug, "->", d.get("name"), "段", len(d.get("sections") or []),
          "链出", len(d.get("links") or []))
