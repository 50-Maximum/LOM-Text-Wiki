# -*- coding: utf-8 -*-
"""盘点缺口：选项有没有文案、事件名字有多弱、触发条件缺多少；同时列出可用的游戏数据源。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row

print("== 选项 ==")
n_opt = con.execute("select count(*) from branch_nodes where kind='choose'").fetchone()[0]
no_text = con.execute("select count(*) from branch_nodes where kind='choose' and (text is null or text='' or text like '选项%')").fetchone()[0]
print("选项节点 %d，其中无文案/占位 %d" % (n_opt, no_text))
for r in con.execute("select script,seq,text from branch_nodes where kind='choose' and (text is null or text='' or text like '选项%') limit 5"):
    print("   %s#%s %r" % (r["script"], r["seq"], r["text"]))

print("\n== 事件 ==")
print("事件条目:", con.execute("select count(*) from pages where type='事件'").fetchone()[0])
weak = con.execute("select count(*) from pages where type='事件' and (name like '%事件%' or name like '转场%' or name like '结果%' or length(name)<=3)").fetchone()[0]
print("名字偏弱:", weak)
for r in con.execute("select name,slug from pages where type='事件' and (name like '%事件%' or length(name)<=3) limit 6"):
    print("   ", r["name"])

print("\n== 场景标题 ==")
print("无标题场景:", con.execute("select count(*) from scenes where title is null or title=''").fetchone()[0])
print("0 句场景:", con.execute("select count(*) from scenes where line_count=0").fetchone()[0])

print("\n== 数据源 ==")
raw = os.path.join(BASE, "data", "raw")
for d in sorted(os.listdir(raw)):
    p = os.path.join(raw, d)
    if os.path.isdir(p):
        print("  raw/%s  %d 文件" % (d, len(os.listdir(p))))
    else:
        print("  raw/%s  %.1f KB" % (d, os.path.getsize(p) / 1024))

plug = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins"
if os.path.isdir(plug):
    print("\n== BepInEx 插件 ==")
    for b, ds, fs in os.walk(plug):
        rel = os.path.relpath(b, plug)
        for f in fs:
            p = os.path.join(b, f)
            print("  %-52s %8.1f KB" % (os.path.join(rel, f), os.path.getsize(p) / 1024))
