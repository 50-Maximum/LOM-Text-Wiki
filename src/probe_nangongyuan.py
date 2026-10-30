# -*- coding: utf-8 -*-
"""找「南宫远就任武林盟主」页，看 O_6_6_2_Break_01_014 出现在哪里、原文是什么。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

for r in c.execute("""select slug,type,lead,sections from pages
                      where name like '%南宫远%' and name like '%盟主%'"""):
    print("页:", r[0], "|", r[1])
    print(" lead:", r[2])
    for s in json.loads(r[3] or "[]"):
        print("  --", s.get("h"))
        for x in (s.get("rows") or [])[:10]:
            print("     ", (x.get("note") or "")[:110], "|", x.get("script") or "", x.get("title") or "")

print("\n=== O_6_6_2_Break_01_014 在 choices 表")
for r in c.execute("""select script,seq,options from choices where options like '%O_6_6_2_Break_01_014%'"""):
    print(" ", r[0], r[1])
    print("  ", r[2][:600])

print("\n=== 该剧本 ch6_6_2_break_start_01 的选项块")
for r in c.execute("select script,var,choicevar,prompt,options from (select 1)"):
    pass
d = json.load(open(B + r"\data\choice_branch.json", encoding="utf-8"))
print(json.dumps(d.get("ch6_6_2_break_start_01"), ensure_ascii=False, indent=1)[:1500])
