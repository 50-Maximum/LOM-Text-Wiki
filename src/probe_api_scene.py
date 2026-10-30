# -*- coding: utf-8 -*-
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
u = "http://127.0.0.1:8765/api/page?slug=" + urllib.parse.quote("场景/ch5_6_5_3")
d = json.loads(urllib.request.urlopen(u, timeout=15).read().decode("utf-8"))
print("段:", [s.get("h") for s in d["sections"]])
for s in d["sections"]:
    if s.get("h") == "剧情衔接":
        for r in s.get("rows") or []:
            print("  行:", r.get("note"), "｜", r.get("script"), "｜", r.get("title"))
    if s.get("h") == "分支选项":
        for b in s.get("choice_rows") or []:
            print("  问:", (b.get("prompt") or "")[:30], "free=", b.get("free"))
            for o in b.get("options") or []:
                print("    -", o.get("text"), "|", o.get("cond") or "无", "|", o.get("result"), "| term=", o.get("terminal"))
