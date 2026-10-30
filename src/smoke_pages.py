# -*- coding: utf-8 -*-
"""各类型页面抽查：字段完整、链接可解析。"""
import json, urllib.request, urllib.parse, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = "http://127.0.0.1:8765"

def g(p):
    return json.loads(urllib.request.urlopen(B + p, timeout=20).read())

types = g("/api/types")["types"]
for t in types:
    rows = g("/api/pages?type=" + urllib.parse.quote(t["type"]) + "&limit=1")["rows"]
    if not rows:
        print(f"{t['type']:<6} 无条目"); continue
    slug = rows[0]["slug"]
    d = g("/api/page?slug=" + urllib.parse.quote(slug))
    bad = 0
    for l in d.get("links", []):
        if not l.get("name"):
            bad += 1
    print(f"{t['type']:<6} {t['n']:>5} 条  样例《{d['name']}》  "
          f"段落 {[s['h'] for s in d['sections']]}  链接 {len(d.get('links',[]))}  失效指向 {bad}")

print()
# 关系页链接双向
d = g("/api/page?slug=" + urllib.parse.quote("人物/唐默铃"))
rel = [x for x in d["links"] if x["kind"] == "关系"]
print("唐默铃 关系", len(rel), [(x["name"], x["label"]) for x in rel[:4]])
back = [x for x in d["backlinks"] if x["kind"] == "关系"]
print("链入关系", len(back))
