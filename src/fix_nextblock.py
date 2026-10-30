# -*- coding: utf-8 -*-
"""把误插到事件页的「接下来」块挪到场景页。"""
import io, re, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

start = s.find("    _nxt = (NXT.get(script) or {})")
endmark = '    secs.append({"h": "接下来", "rows": _jrows})'
end = s.find(endmark)
assert start > 0 and end > start, "找不到误插块"
end += len(endmark)
block = s[start:end]
s = s[:start] + s[end:]
print("已移除误插块", len(block), "字节")

# 场景页锚点：_segid = SEGOF.get(script) 之后的 剧情衔接 append
anchor = '    _segid = SEGOF.get(script) or ""'
i = s.find(anchor)
assert i > 0, "找不到场景页锚点"
j = s.find('        secs.append({"h": "剧情衔接", "rows": _cr})', i)
assert j > 0, "找不到场景页衔接行"
j = s.find("\n", j) + 1
s = s[:j] + block + "\n" + s[j:]
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("已插入场景页，syntax ok")
