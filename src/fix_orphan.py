# -*- coding: utf-8 -*-
"""删除 openChar 替换后遗留的孤立函数体。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\web\index.html"
s = open(p, encoding="utf-8").read()

mark = '  let h=`<h1>${esc(d.name)}</h1><div class="meta">${d.lines} 句台词'
i = s.find(mark)
if i < 0:
    print("未找到残体起点")
else:
    j = s.find("\nasync function ", i)
    if j < 0:
        print("未找到下一个函数")
    else:
        removed = s[i:j]
        s = s[:i] + "\n" + s[j:]
        open(p, "w", encoding="utf-8").write(s)
        print("已删除", len(removed), "字符")
