# -*- coding: utf-8 -*-
import io, sys, json, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = "http://127.0.0.1:8765"


def get(p):
    return json.load(urllib.request.urlopen(B + p, timeout=15))


for slug in ("事件/叶云裳初尝杀孽", "剧情段/S133", "场景/S0208_02_04"):
    try:
        d = get("/api/page?slug=" + urllib.parse.quote(slug))
    except Exception as e:
        print(slug, "取页失败", e)
        continue
    print("==", slug, "|", d.get("name"), "|", d.get("facet2"))
    got = False
    for s in d.get("sections") or []:
        if s.get("h") == "剧情衔接":
            got = True
            print("   [剧情衔接]")
            for r in s["rows"]:
                print("     -", (r.get("title") or r.get("note"))[:44],
                      "→", r.get("slug") or r.get("script"))
    if not got:
        print("   没有剧情衔接段；段名：", [s.get("h") for s in d.get("sections") or []])
