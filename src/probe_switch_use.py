# -*- coding: utf-8 -*-
"""看 ch6_7_1 里 Switch 的用法，以及现有页面对条件的展示。"""
import io, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
p = os.path.join(RAW, "ch6_7_1.txt")
print("脚本存在:", os.path.exists(p))
s = open(p, encoding="utf-8", errors="ignore").read() if os.path.exists(p) else ""
for m in re.finditer(r'.{0,120}(Ch_6_7_1_00[456]).{0,200}', s, re.S):
    print("---")
    print(m.group(0).replace("\n", " ")[:320])

con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
r = con.execute("select slug,name,sections from pages where name like '%南宫远就任%'").fetchone()
print("\n页面:", r["slug"] if r else "无")
if r:
    for sec in json.loads(r["sections"] or "[]"):
        if sec.get("h") in ("剧情衔接", "分支与后果", "场景信息"):
            print("\n==", sec.get("h"))
            if sec.get("html"):
                print(sec["html"][:400])
            for x in (sec.get("rows") or [])[:6]:
                print("   ", str(x)[:220])
            for x in (sec.get("choices") or [])[:4]:
                print("   choice:", str(x)[:200])
