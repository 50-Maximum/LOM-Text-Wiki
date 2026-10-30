# -*- coding: utf-8 -*-
"""接口复查：事件页地点是否带依据，场景页场景信息是否标依据。"""
import io, sys, json, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def page(slug):
    u = "http://127.0.0.1:8765/api/page?slug=" + urllib.parse.quote(slug)
    return json.loads(urllib.request.urlopen(u, timeout=15).read().decode("utf-8"))


for slug in ("事件/晁和炼丹房偷加材料爆炸", "事件/赵活力挫青城长老", "场景/S0108_01"):
    d = page(slug)
    if d.get("error"):
        print(slug, "→ 无此页")
        continue
    print("\n", slug)
    print("  发生地:", (d.get("infobox") or {}).get("发生地"))
    for s in d.get("sections") or []:
        if s.get("h") in ("场景信息", "发生场景"):
            if s.get("html"):
                print("  ", s["h"], ":", s["html"][:120])
            for r in (s.get("rows") or [])[:3]:
                print("  ", s["h"], "|", r.get("note"))
