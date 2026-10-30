# -*- coding: utf-8 -*-
import io, sys, sqlite3, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("地图事件总数:", c.execute("select count(*) from pages where type='地图事件'").fetchone()[0])
print("带条件:", c.execute("select count(*) from pages where type='地图事件' and sections like '%触发条件%'").fetchone()[0])
print("带地点:", c.execute("select count(*) from pages where type='地图事件' and infobox like '%地点%'").fetchone()[0])
print("有对应剧本:", c.execute("select count(*) from pages where type='地图事件' and infobox like '%对应剧本%'").fetchone()[0])
for slug in ("地图事件/Alchemy_Work_E_01", "地图事件/Back_02_E_01", "地图事件/Section_01_07_02_S_01"):
    r = c.execute("select name,lead,infobox,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print("缺", slug); continue
    print("\n==", r[0])
    print(" 导语:", r[1][:110])
    print(" 信息框:", r[2][:170])
    for s in json.loads(r[3])[:3]:
        print("  [%s] %s" % (s.get("h"), [x.get("note", "")[:36] for x in (s.get("rows") or [])][:3]))
try:
    d = json.load(urllib.request.urlopen("http://127.0.0.1:8765/api/pages?type=%E5%9C%B0%E5%9B%BE%E4%BA%8B%E4%BB%B6&limit=3", timeout=8))
    print("\n接口返回:", d.get("total"), [r["name"] for r in d.get("rows", [])][:3])
except Exception as e:
    print("\n接口异常:", e)
