# -*- coding: utf-8 -*-
import io, sys, json, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = "http://127.0.0.1:8765"


def get(p):
    return json.load(urllib.request.urlopen(B + p, timeout=15))


# 找一个主线段内有多个场景的事件
for slug in ("事件/唐惟元急寻赵活买牛", "事件/叶云舟出剑斩杀歹人"):
    d = get("/api/page?slug=" + urllib.parse.quote(slug))
    print("==", slug, "|", d.get("name"), "|", d.get("facet2"))
    for s in d.get("sections") or []:
        if s.get("h") == "剧情衔接":
            for r in s["rows"]:
                print("   ", (r.get("title") or r.get("note"))[:46])
print("\n事件主/支线：", get("/api/facets?type=" + urllib.parse.quote("事件") + "&dim=2"))
print("剧情段主/支线：", get("/api/facets?type=" + urllib.parse.quote("剧情段") + "&dim=2"))
