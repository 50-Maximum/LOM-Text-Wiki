# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== 势力页（含关键词）")
for nm, m in c.execute("""select name,mentions from pages where type='势力'
                          and (name like '%宋%' or name like '%朝廷%' or name like '%官方%'
                               or name like '%千灯%' or name like '%官府%') order by mentions desc"""):
    print("   %-10s %d" % (nm, m))
print("\n=== 前缀为 宋军/朝廷/官方 的人物")
for fc, n in c.execute("""select facet,count(*) from pages where type='人物' and hidden=0
                          and facet in ('宋军','朝廷','官方','金国') group by 1"""):
    print("   %-6s %d" % (fc, n))
print("\n=== 丁护卫 / 杏花仙 / 叶家兄妹 现状")
for nm in ("丁护卫", "杏花仙", "瑞杏", "叶家兄妹", "叶云舟", "叶云裳"):
    r = c.execute("select slug,type,mentions,hidden from pages where name like ? limit 1",
                  ("%" + nm,)).fetchone()
    print("   %-6s %s" % (nm, r))
print("\n=== 千灯楼 台词")
for r in c.execute("select script,seq,speaker,text from lines where text like '%千灯楼%' limit 8"):
    print("   [%s#%s %s] %s" % (r[0], r[1], r[2], r[3][:90].replace("\n", " ")))
print("   共", c.execute("select count(*) from lines where text like '%千灯楼%'").fetchone()[0], "句")
