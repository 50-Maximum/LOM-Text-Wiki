# -*- coding: utf-8 -*-
import io, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("势力页 %d / 人物页 %d / 总页 %d" % (
    c.execute("select count(*) from pages where type='势力'").fetchone()[0],
    c.execute("select count(*) from pages where type='人物'").fetchone()[0],
    c.execute("select count(*) from pages").fetchone()[0]))
cnt = collections.Counter()
for r in c.execute("select name from pages where type='人物'"):
    p = r["name"].split("·")[0] if "·" in r["name"] else "（无）"
    cnt[p] += 1
print("\n人物前缀分布：")
for k, v in cnt.most_common():
    print("   %-8s %d" % (k, v))
for nm in ["千灯楼·杨玄奇", "千灯楼·申屠龙", "丐帮·青蛇老怪", "唐门·唐娇娇", "大理·段智秀", "金国·裘志攘", "泥教·车轩辕", "泥教·刘颚", "丐帮·李相公", "全真派·王喆"]:
    r = c.execute("select name,title from pages where type='人物' and name=?", (nm,)).fetchone()
    print("   %-14s %s" % (nm, ("称号 " + (r["title"] or "-")) if r else "无页"))
