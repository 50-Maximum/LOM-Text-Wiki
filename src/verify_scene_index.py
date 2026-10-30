# -*- coding: utf-8 -*-
"""核验：/api/scenes 是否含这些脚本，前端「脚本直接命中」能否成立。"""
import io, json, sys, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

r = json.loads(urllib.request.urlopen("http://127.0.0.1:8765/api/scenes", timeout=60)
               .read().decode("utf-8"))
sc = {s["script"]: s for s in r.get("scenes") or []}
print("场景总数", len(sc))
for k in ("ch3_5_3_7_1", "S9904_01", "ch4_4_1", "ch5_4_2"):
    s = sc.get(k)
    print("  %-14s %s" % (k, ("OK " + str(s.get("title")) + " / " + str(s.get("chapter"))
                              + " / " + str(s.get("line_count")) + " 句") if s else "缺失"))

for slug in ("场景/ch3_5_3_7_1", "场景/S9904_01"):
    u = "http://127.0.0.1:8765/api/page?slug=" + urllib.parse.quote(slug)
    d = json.loads(urllib.request.urlopen(u, timeout=20).read().decode("utf-8"))
    print("页面", slug, "->", d.get("name") or d.get("error"))
    for sec in d.get("sections") or []:
        if sec.get("h") == "场景信息" and sec.get("html"):
            print("   ", sec["html"][:120])
