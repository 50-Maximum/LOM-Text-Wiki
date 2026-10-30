# -*- coding: utf-8 -*-
"""第 3 批部署后的核验。"""
import io, json, sqlite3, sys, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
n1 = c.execute("select count(*) from pages where sections like ? or infobox like ?",
               ("%人工核定%", "%人工核定%")).fetchone()[0]
n2 = c.execute("select count(*) from pages where sections like ? or infobox like ?",
               ("%证据不足%", "%证据不足%")).fetchone()[0]
print("页面含「人工核定」:", n1)
print("页面含「证据不足」:", n2)

url = "http://127.0.0.1:8765/api/page?slug=" + urllib.parse.quote("场景/ch5_4_2")
d = json.loads(urllib.request.urlopen(url, timeout=20).read().decode("utf-8"))
print("页面:", d.get("name"))
for s in d.get("sections") or []:
    for r in (s.get("rows") or []):
        if r.get("script") in ("ch5_4_2", "S0703_01", "S0101_01"):
            print("  %s | %s" % (s.get("h"), r.get("note")))
