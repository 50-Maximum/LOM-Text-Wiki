# -*- coding: utf-8 -*-
"""一次性核对本轮改动涉及的地点/场景现状。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

WANT = ["唐门禁地", "谷底", "崆峒山村", "鬼岛", "鬼岛海盗洞", "南沟", "南沟集",
        "瑞笙豆浆店", "豆浆店", "青楼", "孤云山", "宣州孤云山", "安济坊",
        "烟花阁", "花月楼", "酒窖", "野狐桥", "飞升宫", "栖霞太虚观",
        "村子里的磨坊", "山村野店", "山店", "山涧", "府衙牢房", "慈云庵",
        "无为寺", "朱家葱肉包摊", "李记烧腊铺", "青霞巷", "福聚楼",
        "朝天门", "药王洞", "钻羊洞", "铁盘岭", "弹筝湖", "真乘寺",
        "七龙女池", "上官交引舖", "临镇", "老虎山", "新竹别第", "火炎山",
        "卧云岗", "小梅村", "画舫", "金乌", "金乌上人"]
print("=== 地点页现状 ===")
for w in WANT:
    rows = list(c.execute("select slug,name,type,facet from pages where name=?", (w,)))
    if rows:
        for r in rows:
            print("  %-10s %-22s %-6s facet=%s" % (w, r["slug"], r["type"], r["facet"]))
    else:
        print("  %-10s （无条目）" % w)

print("\n=== 场景 S2321_02_01 ===")
r = c.execute("select script,title,chapter,place,line_count,cjk from scenes where script=?",
              ("S2321_02_01",)).fetchone()
print("  scenes 表:", dict(r) if r else "无记录")
n = c.execute("select count(*) from lines where script=?", ("S2321_02_01",)).fetchone()[0]
print("  lines 条数:", n)
p = c.execute("select slug,name from pages where slug=?", ("场景/S2321_02_01",)).fetchone()
print("  页面:", (p["slug"], p["name"]) if p else "无页面")

print("\n=== facet 现状（地点·区域） ===")
for r in c.execute("""select facet, count(*) n from pages where type='地点'
                      and slug not in (select slug from place_children)
                      group by facet order by n desc"""):
    print("  %-10s %d" % (r["facet"], r["n"]))
