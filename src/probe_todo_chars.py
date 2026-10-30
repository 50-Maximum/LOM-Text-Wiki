# -*- coding: utf-8 -*-
"""列出还没写定稿简介的人物（无 footnotes 或简介过短），按笔记条数排序。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
intro = json.load(open(B + r"\intros_char.json", encoding="utf-8"))
hidden = set(json.load(open(B + r"\chars_hidden.json", encoding="utf-8")) or [])

done = {k for k, v in intro.items()
        if isinstance(v, dict) and (v.get("footnotes") or [])}
print("已定稿（带脚注）%d / 简介条目 %d" % (len(done), len(intro)))

cnt = dict(c.execute("""select name,count(*) from notes where type='人物' group by name"""))
todo = [(n, k) for n, k in cnt.items() if k >= 6]
todo = [(n, k) for n, k in todo if n not in ("赵活",)]
todo.sort(key=lambda x: -x[1])
print("\n待做（笔记≥6，按条数）：")
i = 0
for n, k in todo:
    if n in done:
        continue
    print("  %-10s 笔记%-4d %s" % (n, k, "隐藏" if n in hidden else ""))
    i += 1
    if i >= 30:
        break
print("\n合计待做 %d" % sum(1 for n, k in todo if n not in done))
