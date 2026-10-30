# -*- coding: utf-8 -*-
"""① S0022_01 改判唐门；② 删除该场错误来源（scenes.place 锦香宫）。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")

P = os.path.join(D, "place_manual.json")
m = json.load(open(P, encoding="utf-8"))
m["S0022_01"] = {"place": "唐门", "src": "人工指定"}
json.dump(m, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("已写入人工指定：S0022_01 → 唐门")

con = sqlite3.connect(os.path.join(D, "wiki.db"))
old = con.execute("select place from scenes where script='S0022_01'").fetchone()[0]
con.execute("update scenes set place='' where script='S0022_01'")
con.commit()
print("已清除错误来源 scenes.place:", old, "→ 空")
print("剩余场景数:", con.execute("select count(*) from scenes").fetchone()[0])
con.close()
