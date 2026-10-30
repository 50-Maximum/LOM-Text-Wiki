# -*- coding: utf-8 -*-
"""① 列出现有地点页名（含子级）供映射；② 检查待用名是否存在；③ 统计无标题/泛标题场景。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row

names = sorted(r[0] for r in con.execute("select name from pages where type='地点'"))
print("地点页共", len(names))

want = ["唐门-炼丹房", "唐门-弟子房", "唐门-讲经堂", "唐门-后山", "唐门-练功场",
        "唐门-正心堂", "崆峒-半雨屏", "崆峒-飞天殿", "崆峒-大铁铺", "崆峒-铁拳巷",
        "崆峒-镇魂狱", "崆峒-夺魄森林", "老虎山", "无色广场赌坊", "无色广场",
        "襄阳", "大雪山", "青城山", "眉山镇", "江陵", "崆峒山", "唐门"]
print("\n待用名存在性:")
for w in want:
    print("   %-12s %s" % (w, "有" if w in names else "缺"))

subs = [n for n in names if "-" in n]
print("\n现有子级地点（%d）:" % len(subs))
print("   " + "、".join(subs))

# 无标题 / 泛标题
GEN = {"结果", "这是因为", "你的领悟", "你的干劲", "你的决心", "你的勇气", ""}
rows = con.execute("select script,title,chapter,line_count from scenes").fetchall()
no_t = [r["script"] for r in rows if not (r["title"] or "").strip()]
gen_t = [r["script"] for r in rows if (r["title"] or "").strip() in GEN]
print("\n场景总数:", len(rows), "无标题:", len(no_t), "泛标题:", len(gen_t))
print("泛标题样例:", [(r["script"], r["title"]) for r in rows if (r["title"] or "") in GEN][:10])
