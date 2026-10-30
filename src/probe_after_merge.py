# -*- coding: utf-8 -*-
"""合并后终检：重定向、坏链、导语、前缀。"""
import io, sys, sqlite3, json, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = "http://127.0.0.1:8765"
db = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect("file:" + db.replace("\\", "/") + "?mode=ro", uri=True).cursor()
print("页面", c.execute("select count(*) from pages").fetchone()[0],
      "| 人物", c.execute("select count(*) from pages where type='人物'").fetchone()[0],
      "| 别名", c.execute("select count(*) from aliases").fetchone()[0],
      "| 重定向", c.execute("select count(*) from redirects").fetchone()[0])
print("坏链", c.execute("""select count(distinct dst) from links
      where not exists(select 1 from pages p where p.slug=links.dst)""").fetchone()[0])
print("无导语", c.execute("select count(*) from pages where lead is null or lead=''").fetchone()[0])
print("无前缀人物", c.execute("select count(*) from pages where type='人物' and name not like '%·%'").fetchone()[0])
for alias in ("人物/唐掌门", "人物/黑衣前辈", "人物/唐二侠", "人物/大师兄", "人物/高和"):
    d = json.load(urllib.request.urlopen(B + "/api/page?slug=" + urllib.parse.quote(alias), timeout=15))
    print("  %-14s → %s" % (alias, d.get("name")))
