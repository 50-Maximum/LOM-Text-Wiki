# -*- coding: utf-8 -*-
import io, sys, sqlite3, re, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("唐门招新 scripts 列:", c.execute("select scripts from guide_index where name='唐门招新'").fetchone())
print("\n万里鹏程挑战赵活 所在脚本:", c.execute("select distinct script from notes where name='万里鹏程挑战赵活'").fetchall())
print("丐帮赖账被泼茶驱赶 脚本:", c.execute("select distinct script from notes where name='丐帮赖账被泼茶驱赶'").fetchall())
print("\n全部脚本文件名数:", len(glob.glob(r"D:\LegendOfMortal Wiki\data\raw\scripts\*.txt")))
names = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(r"D:\LegendOfMortal Wiki\data\raw\scripts\*.txt")}
print("scene_time 里脚本存在比例:", end=" ")
rows = c.execute("select script from scene_time").fetchall()
print(sum(1 for (s,) in rows if s in names), "/", len(rows))
print("\nguide_index scripts 列样例 10:")
for nm, sc in c.execute("select name,scripts from guide_index limit 10"):
    print("  ", nm, "|", str(sc)[:100])
