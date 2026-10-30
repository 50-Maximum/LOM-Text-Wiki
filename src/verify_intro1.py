# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("人物页", c.execute("select count(*) from pages where type='人物'").fetchone()[0],
      "总页", c.execute("select count(*) from pages").fetchone()[0])
for nm in ["市井·曾文", "江湖·方独弱", "朝廷·孟政宗", "丐帮·李相公", "点苍派·徐光辉",
           "唐门·唐与黥", "锦香宫·乔师妹", "市井·少女", "泥教·白鸿", "丐帮·阿叔"]:
    r = c.execute("select name,substr(lead,1,70) as ld from pages where type='人物' and name=?", (nm,)).fetchone()
    print("  %-16s %s" % (nm, (r["ld"] or "") if r else "无页"))
print("\n残留占位页：")
for nm in ["江湖·赵某", "市井·赵某", "铁拳门·掌门", "玄功门·掌门", "市井·白兄"]:
    r = c.execute("select name from pages where type='人物' and name=?", (nm,)).fetchone()
    print("   %-14s %s" % (nm, "仍在" if r else "已清"))
print("\n仍在用模板话术的人物页：",
      c.execute("select count(*) from pages where type='人物' and lead like '%原文中出现%'").fetchone()[0])
