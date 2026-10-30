# -*- coding: utf-8 -*-
"""关闭投票：阶段只认人工表、章节、旗标/条件与原文；判不出就留不限时间。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

start = s.index("def arc_vote(script):")
end = s.index("def arc_of(script):")
new_fn = '''def arc_vote(script):
    """投票已停用：阶段改由人工表、章节、旗标条件与原文判定。"""
    return ""


'''
s = s[:start] + new_fn + s[end:]
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("arc_vote 已停用")
