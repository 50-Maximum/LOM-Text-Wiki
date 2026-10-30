# -*- coding: utf-8 -*-
"""看泛称词在 aliases 里都指向哪一页，判断该不该继续自动链接。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
GENERIC = ["掌门", "长老", "师兄", "师姐", "师弟", "师妹", "师父", "弟子", "妇人", "路人",
           "乞丐", "店小二", "大妈", "大汉", "老者", "少年", "女孩", "男子", "女子",
           "家丁", "护卫", "官兵", "差役", "掌柜", "老板", "客人", "众人", "旁白", "汉子",
           "师父", "老丈", "姑娘", "少侠", "小厮", "侍女", "丫鬟", "仆役", "马车夫"]
for g in dict.fromkeys(GENERIC):
    rows = list(c.execute("select slug from aliases where alias=?", (g,)))
    for (slug,) in rows:
        nm = c.execute("select name,type from pages where slug=?", (slug,)).fetchone()
        print("  %-6s → %-22s %s" % (g, slug, nm if nm else "（页不存在）"))
