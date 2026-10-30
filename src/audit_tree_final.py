# -*- coding: utf-8 -*-
"""重构后一致性核查：三级链、筛选档、其他组、上级/下辖互指。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

def page(nm):
    r = c.execute("select lead,infobox,sections from pages where type='地点' and name=?",
                  (nm,)).fetchone()
    if not r:
        return None
    return json.loads(r[1] or "{}"), [x.get("h") for x in json.loads(r[2] or "[]")]

print("=== 三级链")
for nm in ("青城山", "青城-青城山镇", "都江客栈", "岳阳", "锦香宫", "华音阁", "川蜀", "眉山", "唐门"):
    inf = page(nm)
    if not inf:
        print("  %-14s 无页" % nm)
        continue
    print("  %-14s 上级=%-12s 下辖=%s" % (nm, inf[0].get("上级") or "-", inf[0].get("下辖") or "-"))

print("\n=== 筛选档（地点）")
for f, n in c.execute("""select facet, count(*) from pages where type='地点' and hidden=0
                         group by facet order by 2 desc"""):
    print("  %-10s %d" % (f or "（空）", n))

print("\n=== facet=其他 里是否混进了有子级的地点")
par = json.load(open(B + r"\data\places_fix.json", encoding="utf-8")).get("parent", {})
kids = set(par.values())
bad = [r[0] for r in c.execute("""select name from pages where type='地点' and facet='其他'""")
       if r[0] in kids]
print("  混入:", bad or "无")

print("\n=== 上级字段里的名字是否都有对应页面")
names = {r[0] for r in c.execute("select name from pages where type='地点'")}
miss = sorted({v for v in par.values() if v not in names})
print("  缺页上级:", miss or "无")
