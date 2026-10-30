# -*- coding: utf-8 -*-
import io, sys, json, urllib.parse, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = "http://127.0.0.1:8765"
for q in ["赵活", "心相", "唐门", "叶云舟", "江湖快报", "降龙", "小师妹"]:
    u = BASE + "/api/search2?q=" + urllib.parse.quote(q)
    try:
        d = json.load(urllib.request.urlopen(u, timeout=10))
    except Exception as e:
        print(q, "ERR", e); continue
    pages = [(p.get("name"), p.get("type")) for p in (d.get("pages") or [])][:3]
    scenes = [(s.get("title") or s.get("script")) for s in (d.get("scenes") or [])][:2]
    print("%-6s 条目%d 场景%d 原文%d  | %s | %s" % (
        q, len(d.get("pages") or []), len(d.get("scenes") or []), len(d.get("lines") or []),
        pages, scenes))
