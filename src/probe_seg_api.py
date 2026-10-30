# -*- coding: utf-8 -*-
import io, sys, json, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = "http://127.0.0.1:8765"


def get(p):
    return json.load(urllib.request.urlopen(B + p, timeout=15))


for slug in ("剧情段/S012", "剧情段/S001"):
    d = get("/api/page?slug=" + urllib.parse.quote(slug))
    print("==", slug, "|", d.get("name"))
    print("   导语:", (d.get("lead") or "")[:90])
    for s in d.get("sections") or []:
        print("   [%s]" % s.get("h"), len(s.get("rows") or []), "行")
        for r in (s.get("rows") or [])[:3]:
            print("      -", (r.get("title") or r.get("note") or "")[:44],
                  "|", r.get("slug") or r.get("script"))
print("\n类型计数:", [(x["type"], x["n"]) for x in get("/api/types")["types"]][:8])
