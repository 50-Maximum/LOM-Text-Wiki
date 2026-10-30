# -*- coding: utf-8 -*-
"""命中明细：年表行来自 calendar.json（109 条），不是 timeline.json（24 条）。"""
import io, sys, json, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
ref = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
cal = json.load(open(B + r"\ref_wiki\calendar.json", encoding="utf-8"))
print("calendar 字段:", list(cal[0].keys()) if cal else "-")
print("样例:", json.dumps(cal[0], ensure_ascii=False)[:220] if cal else "-")

titles = dict(c.execute("select script,title from scenes"))
cho = list(c.execute("select script,seq,options from choices"))
txt = list(c.execute("select script,seq,text from lines"))

def quotes(ev):
    out = []
    for m in re.findall(r"「([^」]{2,26})」", ev or ""):
        s = re.sub(r"^[（(].*?[）)]", "", m.strip()).strip()
        if s and s not in out:
            out.append(s)
    return out

# 年表行文本 = 事件名 + 备注（选项写在哪一列待确认）
rows = []
for r in cal:
    blob = " ".join(str(r.get(k) or "") for k in r)
    rows.append(blob)
print("行数", len(rows))
