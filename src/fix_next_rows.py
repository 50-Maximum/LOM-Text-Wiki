# -*- coding: utf-8 -*-
"""修「接下来」：连接未设 Row 工厂，改用元组解包。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''        for _e in c.execute("""select dst,type,cond,switch,result,site from scene_edges
                               where src=? order by type, site, result""", (script,)):
            _dst, _ty = _e["dst"], _e["type"]'''
new = '''        for _r in c.execute("""select dst,type,cond,switch,result,site from scene_edges
                               where src=? order by type, site, result""", (script,)):
            _dst, _ty, _cond, _sw, _res, _site = _r'''
assert old in s, "锚点1"
s = s.replace(old, new, 1)

s = s.replace('if _e["switch"]:', 'if _sw:', 1)
s = s.replace('_bits.append("判定 %s 结果 %s" % (_e["switch"], _e["result"]))',
              '_bits.append("判定 %s 结果 %s" % (_sw, _res))', 1)
s = s.replace('if _e["cond"]:', 'if _cond:', 1)
s = s.replace('_bits.append(_e["cond"].replace("switch", "判定")',
              '_bits.append(_cond.replace("switch", "判定")', 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("已修正，剩余 _e[ 引用:", s.count('_e["'))
