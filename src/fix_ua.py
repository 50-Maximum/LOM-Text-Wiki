# -*- coding: utf-8 -*-
"""把 updater 的 UA 改为纯 ASCII（中文 UA 会让 http.client 抛 UnicodeEncodeError）。"""
p = r"D:\LegendOfMortal Wiki\src\updater.py"
s = open(p, encoding="utf-8").read()
s = s.replace('headers={"User-Agent": "%s/%s" % (APP_NAME, local_version())}',
              'headers={"User-Agent": "LoMWiki/%s" % local_version()}')
open(p, "w", encoding="utf-8").write(s)
print("剩余中文 UA:", s.count('APP_NAME, local_version()'), "｜ASCII UA:", s.count("LoMWiki/"))
