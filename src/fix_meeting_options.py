# -*- coding: utf-8 -*-
"""修 meeting 类选项文案：脚本里 meet[n] = 条件 and "event+我想去青城派留学+0+0" or "~x"。

把 branch_nodes / choices 里残留的「选项N」换成真实文案。
"""
import os, sys, io, re, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

RX = re.compile(r'(\w+)\[(\d+)\]\s*=\s*(.*?)"([^"]*)"')

pairs = {}   # (script, idx) -> text
for fn in sorted(os.listdir(RAW)):
    if not fn.endswith(".txt"):
        continue
    sid = fn[:-4]
    for ln in open(os.path.join(RAW, fn), encoding="utf-8"):
        m = RX.search(ln)
        if not m:
            continue
        var, idx, mid, txt = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        if "event+" not in txt:
            continue
        seg = [x for x in txt.split("+") if x]
        if len(seg) >= 2 and seg[0] == "event":
            pairs[(sid, idx)] = seg[1]

print("event 型选项", len(pairs))
sample = list(pairs.items())[:6]
for k, v in sample:
    print("  ", k, "->", v)

# 回写 branch_nodes
upd = 0
for script, seq, idx, text in c.execute("""select script,seq,idx,text from branch_nodes
                                          where kind='choose'""").fetchall():
    if text and text.startswith("选项"):
        real = pairs.get((script, idx))
        if real:
            c.execute("update branch_nodes set text=? where script=? and seq=? and idx=?",
                      (real, script, seq, idx))
            upd += 1
print("branch_nodes 更新", upd)

# 回写 choices.options
import json
upd2 = 0
for rid, script, oj in c.execute("select id,script,options from choices").fetchall():
    opts = json.loads(oj or "[]")
    ch = False
    for i, o in enumerate(opts, 1):
        lab = o.get("label") or ""
        if lab.startswith("选项"):
            real = pairs.get((script, i))
            if real:
                o["label"] = real
                o["text"] = real
                ch = True
    if ch:
        c.execute("update choices set options=? where id=?", (json.dumps(opts, ensure_ascii=False), rid))
        upd2 += 1
c.commit()
print("choices 更新", upd2)
