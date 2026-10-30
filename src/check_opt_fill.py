# -*- coding: utf-8 -*-
"""统计选项占位与事件命名缺口，并抽查 S0003_01_02 的选项文案。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

n = c.execute("select count(*) from branch_nodes where kind='choose'").fetchone()[0]
ph = c.execute("select count(*) from branch_nodes where kind='choose' "
               "and (text is null or text='' or text like '选项%')").fetchone()[0]
print("选项节点 %d ／ 占位 %d" % (n, ph))
print("\nS0003_01_02 选项:")
for r in c.execute("select idx,text,cond from branch_nodes where script='S0003_01_02' and kind='choose'"):
    print("   #%s %s（%s）" % (r["idx"], r["text"], r["cond"]))

print("\n占位样例:")
for r in c.execute("select script,idx,text from branch_nodes where kind='choose' "
                   "and (text like '选项%' or text='') limit 6"):
    print("   %s #%s %r" % (r["script"], r["idx"], r["text"]))
