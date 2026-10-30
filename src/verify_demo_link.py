# -*- coding: utf-8 -*-
"""验证：①Demo 限定提示是否挂上 ②「选择」行的索引是否指向选项所在场景"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

print("=== Demo 限定页面数")
print(" ", c.execute("select count(*) from pages where sections like '%内容状态%'").fetchone()[0])
for slug in ("场景/act3_2", "事件/赵活守塔痛打师弟", "地点/唐门-练功塔", "设施/练功塔"):
    r = c.execute("select lead,infobox,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print(" ", slug, "（无页）")
        continue
    inf = json.loads(r[1] or "{}")
    first = (json.loads(r[2] or "[]") or [{}])[0]
    print(" ", slug, "| 内容状态:", inf.get("内容状态"), "| 首段:", first.get("h"),
          "|", (first.get("html") or "")[:40])

print("\n=== 选择行索引")
secs = c.execute("select sections from pages where slug='事件/南宫远就任武林盟主'").fetchone()[0]
for s in json.loads(secs):
    if s.get("h") == "触发条件":
        for r in s.get("rows") or []:
            print("  ", json.dumps({k: r.get(k) for k in ("note", "script", "title", "seq")},
                                   ensure_ascii=False))
