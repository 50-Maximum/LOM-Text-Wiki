# -*- coding: utf-8 -*-
"""实测筛选接口：同一类型带/不带 facet，返回的 total 与条数是否变化。"""
import io, sys, json, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def get(path):
    u = "http://127.0.0.1:8765" + path
    return json.loads(urllib.request.urlopen(u, timeout=15).read().decode("utf-8"))


for typ in ("地点", "人物", "事件"):
    f = get("/api/facets?type=" + urllib.parse.quote(typ))
    f2 = get("/api/facets?type=" + urllib.parse.quote(typ) + "&dim=2")
    print("\n%-4s facets=%s" % (typ, (f.get("facets") or [])[:4]))
    print("     dim2=%s" % ((f2.get("facets") or [])[:4],))
    base = get("/api/pages?type=%s&offset=0&limit=5" % urllib.parse.quote(typ))
    print("     不带筛选 total=%s rows=%d" % (base.get("total"), len(base.get("rows") or [])))
    vs = (f.get("facets") or [])
    if vs:
        v = vs[0]["v"]
        q = get("/api/pages?type=%s&offset=0&limit=5&facet=%s"
                % (urllib.parse.quote(typ), urllib.parse.quote(v)))
        print("     带 facet「%s」total=%s rows=%d" % (v, q.get("total"), len(q.get("rows") or [])))
    vs2 = (f2.get("facets") or [])
    if vs2:
        v2 = vs2[0]["v"]
        q2 = get("/api/pages?type=%s&offset=0&limit=5&facet2=%s"
                 % (urllib.parse.quote(typ), urllib.parse.quote(v2)))
        print("     带 facet2「%s」total=%s rows=%d" % (v2, q2.get("total"), len(q2.get("rows") or [])))
