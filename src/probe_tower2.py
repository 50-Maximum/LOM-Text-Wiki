# -*- coding: utf-8 -*-
"""①练功塔四场戏如何被触发（有没有入边 / 菜单选项 / 设施绑定）②这几场是否进过攻略年表"""
import io, sys, json, sqlite3, re, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

ACTS = ["act1", "act2_1", "act2_3", "act3_2", "act3_4", "act2_3_1", "act2_3_2", "act2_3_3"]

print("=== 场次基本信息")
for a in ACTS:
    r = c.execute("select title,chapter,place,line_count from scenes where script=?", (a,)).fetchone()
    print("  %-10s %s" % (a, r))

print("\n=== 谁跳到这些场（从原始剧本里找 SetNextScript / choose 选项）")
RAW = os.path.join(B, "data", "raw", "scripts")
idx = {}
for f in glob.glob(os.path.join(RAW, "*.txt")):
    sc = os.path.basename(f)[:-4]
    try:
        txt = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for a in ACTS:
        if ('"%s"' % a) in txt or ("+" + a + "+") in txt:
            idx.setdefault(a, []).append(sc)
for a in ACTS:
    print("  %-10s ← %s" % (a, idx.get(a) or "（没有任何剧本引用）"))

print("\n=== 攻略年表 / 剧情段里有没有")
for a in ACTS:
    n1 = c.execute("select count(*) from scene_order where script=?", (a,)).fetchone()[0]
    n2 = c.execute("select count(*) from scene_time where script=?", (a,)).fetchone()[0]
    n3 = c.execute("select count(*) from guide_events where script like ?", ("%" + a + "%",)).fetchone()[0]
    print("  %-10s scene_order=%d scene_time=%d guide_events=%d" % (a, n1, n2, n3))

print("\n=== 设施的练功塔条目")
for r in c.execute("""select ns,eid,title,substr(body,1,300) from entries where title like '%练功塔%'"""):
    print("  ", r)
