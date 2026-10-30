# -*- coding: utf-8 -*-
"""把「条件」也纳入检索：switch_xxx / choice_xxx 这类判定变量也算可搜对象。
输出仍写 web/flags.json，多一个字段 k（旗标 / 条件）。
"""
import io, sys, json, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

out = []
# 旗标
for flag, value, script, seq, branch, title in c.execute("""
        select f.flag, f.value, f.script, f.seq, f.branch, coalesce(s.title,'')
        from flags f left join scenes s on s.script=f.script
        where f.flag<>'' order by f.flag, f.script, f.seq"""):
    out.append({"f": flag, "v": value, "s": script, "q": seq,
                "b": branch or "", "t": title, "k": "旗标"})

# 条件（switch_/choice_ 变量）——来自 story_segments 的分支条件
TOK = re.compile(r"([A-Za-z_]*?(?:switch|choice)[A-Za-z0-9_]*)\s*==\s*(-?\d+)")
SG = json.load(open(B + r"\story_segments.json", encoding="utf-8"))
SEGT = {s["id"]: s.get("title") or "" for s in SG["segments"]}
seen = set()
for s in SG["segments"]:
    for b in (s.get("branches") or []):
        to = b.get("to") or ""
        title = ""
        if to:
            row = c.execute("select title from scenes where script=?", (to,)).fetchone()
            title = row[0] if row else ""
        for name, val in TOK.findall(b.get("cond") or ""):
            key = (name, val, to)
            if key in seen:
                continue
            seen.add(key)
            out.append({"f": name, "v": val, "s": to, "q": 0,
                        "b": "分支去「%s」" % (SEGT.get(s["id"], "")[:12]),
                        "t": title, "k": "条件"})

json.dump(out, open(r"D:\LegendOfMortal Wiki\web\flags.json", "w", encoding="utf-8"),
          ensure_ascii=False)
n_flag = sum(1 for x in out if x["k"] == "旗标")
print("导出 %d 条（旗标 %d、条件 %d）" % (len(out), n_flag, len(out) - n_flag))
for q in ("TC0001", "switch_001", "choice_talk"):
    n = sum(1 for x in out if q.lower() in x["f"].lower())
    print("  「%s」→ %d 条" % (q, n))
