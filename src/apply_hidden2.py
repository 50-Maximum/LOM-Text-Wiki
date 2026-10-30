# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\chars_hidden.json"
h = set(json.load(open(p, encoding="utf-8")))
print("原隐藏", len(h))
h |= {"路人侠", "长老", "公子侠", "女侠", "蒙面人", "武师", "少侠", "火闪电",
      "管家", "护院", "轿夫", "船夫", "小贩", "店家", "镖师", "庄丁", "门房"}
json.dump(sorted(h), open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("新隐藏", len(h))
