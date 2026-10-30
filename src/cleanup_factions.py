# -*- coding: utf-8 -*-
import sqlite3

c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
GENERIC = ("少侠", "通判", "弟子", "众人", "路人", "侠客", "姑娘", "公子",
           "先生", "前辈", "大汉", "汉子", "少年", "少女", "老者", "掌柜",
           "店小二", "侍卫", "护卫", "士兵", "百姓", "村民", "客人", "商人")
for g in GENERIC:
    c.execute("DELETE FROM char_faction WHERE char_id IN (SELECT id FROM names WHERE name=?)", (g,))
c.commit()
print("remaining 上官世家:",
      c.execute("""SELECT n.name FROM char_faction cf JOIN names n ON n.id=cf.char_id
                   WHERE cf.faction='上官世家'""").fetchall())
print("total assigned:", c.execute("SELECT COUNT(*) FROM char_faction").fetchone()[0])
