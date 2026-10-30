# -*- coding: utf-8 -*-
"""看事件页「选择」行的实际字段，以及该剧本 choices 表里的选项块位置。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

secs = c.execute("select sections from pages where slug='事件/南宫远就任武林盟主'").fetchone()[0]
for s in json.loads(secs):
    if s.get("h") == "触发条件":
        for r in s.get("rows") or []:
            print("行:", json.dumps({k: r.get(k) for k in ("note", "script", "title", "seq")},
                                    ensure_ascii=False))

print("\n=== ch6_6_2_break_start_01 的 choices 表")
for r in c.execute("select id,seq,checkpoint,options from choices where script='ch6_6_2_break_start_01'"):
    print("  id=%s seq=%s" % (r[0], r[1]), r[3][:200])

print("\n=== branch_nodes 里 kind=choose 的行")
for r in c.execute("""select seq,idx,text from branch_nodes
                      where script='ch6_6_2_break_start_01' and kind='choose'"""):
    print("  ", r)
