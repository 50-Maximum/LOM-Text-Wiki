# -*- coding: utf-8 -*-
"""把 choices.options 里残留的 O_xxx 代码换成中文台词。

来源 data/build/text.json（80,301 键）。改完回写 choices.options。
用法: python fix_choice_text.py [--dry]
"""
import os, sys, io, sqlite3, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
DB = os.path.join(BASE, "data", "wiki.db")
TEXT = os.path.join(BASE, "data", "build", "text.json")

dry = "--dry" in sys.argv
table = json.load(open(TEXT, encoding="utf-8"))
RX_CODE = re.compile(r"^O_[A-Za-z0-9_]+$")

c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")
rows = c.execute("select id, script, seq, checkpoint, options from choices").fetchall()

fixed = miss = total_opt = 0
miss_keys = set()
updates = []
for rid, script, seq, cp, oj in rows:
    try:
        opts = json.loads(oj or "[]")
    except Exception:
        continue
    changed = False
    for it in opts:
        total_opt += 1
        code = ""
        for f in ("text", "label", "key"):
            v = (it.get(f) or "").strip()
            if RX_CODE.match(v):
                code = v
                break
        if not code:
            continue
        zh = table.get(code)
        if not zh:
            miss += 1
            miss_keys.add(code)
            continue
        if it.get("text") != zh:
            it["text"] = zh
            changed = True
        if it.get("label") in ("", None) or RX_CODE.match((it.get("label") or "").strip()):
            it["label"] = zh
            changed = True
        if not it.get("key"):
            it["key"] = code
            changed = True
        fixed += 1
    if changed:
        updates.append((json.dumps(opts, ensure_ascii=False), rid))

print(f"选项总数 {total_opt}｜替换 {fixed}｜查不到 {miss}（{len(miss_keys)} 种）")
if miss_keys:
    print("  缺失样本:", list(miss_keys)[:8])
print("待写回行数", len(updates))
if not dry:
    c.executemany("update choices set options=? where id=?", updates)
    c.commit()
    print("已写回")
    # 复测
    left = 0
    for (oj,) in c.execute("select options from choices"):
        if "O_" in (oj or ""):
            left += oj.count('"text": "O_') + oj.count('"label": "O_')
    print("复测残留 O_ 文本:", left)
