# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for kw in ["龙湘持惜花令", "外姓弟子月度评鉴", "赵活提议攻打崆峒"]:
    r = c.execute("select name,sections from pages where type='事件' and name like ?", ("%" + kw + "%",)).fetchone()
    if not r:
        continue
    print("==", r["name"])
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "分支选项":
            cr = s.get("choice_rows") or []
            print("   组数", len(cr))
            for b in cr[:2]:
                print("   题:", (b.get("prompt") or "")[:40])
                for o in (b.get("options") or [])[:3]:
                    print("     -", o.get("text", "")[:26], "| next=", o.get("next"),
                          "| 标题=", o.get("next_title", "")[:20], "| terminal=", o.get("terminal"),
                          "| 结果=", (o.get("result") or "")[:26])
