# -*- coding: utf-8 -*-
"""全胜利归铁拳门（原火炎山剑阁，后投铁拳门）；同时盘点需要重写的简介。"""
import io, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"

cp = json.load(open(os.path.join(B, "chars_prefix.json"), encoding="utf-8"))
cp["全胜利"] = "铁拳门"
json.dump(cp, open(os.path.join(B, "chars_prefix.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("全胜利 → 铁拳门")

c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
rows = [r for r in c.execute("select name,lead from pages where type='人物'")]
bad_kw = ("原文中出现", "未给出成段", "以下为原文摘录", "所给笔记", "笔记未记载",
          "暂无", "待补", "见相关场景", "此人在原文中")
bad, short = [], []
for r in rows:
    t = (r["lead"] or "").strip()
    if any(k in t for k in bad_kw):
        bad.append((r["name"], t[:40]))
    elif len(t) < 25:
        short.append((r["name"], t[:40]))
print("人物页 %d，含模板话术 %d，过短(<25字) %d" % (len(rows), len(bad), len(short)))
print("\n模板话术样例：")
for n, t in bad[:10]:
    print("   %-22s %s" % (n, t))
print("\n过短样例：")
for n, t in short[:10]:
    print("   %-22s %s" % (n, t))
json.dump({"bad": bad, "short": short}, open(os.path.join(B, "research", "intro_todo.json"), "w",
          encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n清单已写 data\\research\\intro_todo.json")
