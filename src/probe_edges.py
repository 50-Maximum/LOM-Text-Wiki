# -*- coding: utf-8 -*-
"""查 scene_edges 是否有数据、row_factory 情况。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("总数:", c.execute("select count(*) from scene_edges").fetchone()[0])
print("ch6_7_1 出向:", c.execute(
    "select dst,type,cond,switch,result from scene_edges where src='ch6_7_1'").fetchall()[:5])
print("S0022_01 出向:", c.execute(
    "select dst,type from scene_edges where src='S0022_01'").fetchall()[:5])
print("列:", [x[1] for x in c.execute("PRAGMA table_info(scene_edges)")])
