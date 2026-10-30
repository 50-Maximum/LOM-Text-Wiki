# -*- coding: utf-8 -*-
"""交付前终检。"""
import io, sys, json, urllib.request, urllib.parse, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = "http://127.0.0.1:8765"


def get(p):
    return json.load(urllib.request.urlopen(B + p, timeout=15))


t = get("/api/types")
print("类型:", [(x["type"], x["n"]) for x in t["types"]][:12])
for slug in ("关于本站", "世界观/总览", "数值/总览", "地图事件/索引", "时间线/按年月", "时间线/总览"):
    d = get("/api/page?slug=" + urllib.parse.quote(slug))
    print("  %-14s 段数 %-3s 导语 %s" % (slug, len(d.get("sections") or []), (d.get("lead") or "")[:34]))

c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("\n页面", c.execute("select count(*) from pages").fetchone()[0],
      "| 链接", c.execute("select count(*) from links").fetchone()[0],
      "| 重定向", c.execute("select count(*) from redirects").fetchone()[0])
print("坏链:", c.execute("""select count(distinct dst) from links
    where not exists(select 1 from pages p where p.slug=links.dst)""").fetchone()[0])
print("无导语:", c.execute("select count(*) from pages where lead is null or lead=''").fetchone()[0])
