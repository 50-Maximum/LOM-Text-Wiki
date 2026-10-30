# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row


def show(kw):
    r = c.execute("select name,facet,infobox,sections from pages where type='事件' and name like ?",
                  ("%" + kw + "%",)).fetchone()
    if not r:
        print("==", kw, "无页")
        return
    inf = json.loads(r["infobox"] or "{}")
    print("== %s｜阶段=%s｜出现阶段=%s" % (r["name"], r["facet"], inf.get("出现阶段", "-")))
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") in ("触发条件", "分支选项"):
            print("   【%s】" % s["h"])
            for rw in (s.get("rows") or [])[:4]:
                print("      -", (rw.get("note") or "")[:70], "→", rw.get("title") or "")
    # 选项是否带 script
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "分支选项":
            n = sum(1 for rw in (s.get("rows") or []) if rw.get("script"))
            print("      可点行数：", n, "/", len(s.get("rows") or []))


for kw in ["赵活提议攻打崆峒", "万里鹏程挑战赵活", "三人道中遇敌拦路",
           "外姓弟子月度评鉴", "段考约战", "龙湘持惜花令"]:
    show(kw)
    print()
