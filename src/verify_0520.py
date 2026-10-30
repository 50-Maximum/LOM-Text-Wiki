# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row


def show(nm, typ="势力"):
    r = c.execute("select name,substr(lead,1,80) as ld,infobox,facet from pages where type=? and name=?",
                  (typ, nm)).fetchone()
    if not r:
        print("  %-8s 无页" % nm)
        return
    inf = json.loads(r["infobox"] or "{}")
    print("  %-8s 上级=%-6s 下辖=%-4s 成员=%-4s 筛=%s" % (
        r["name"], inf.get("上级", "-"), inf.get("下辖", "-"), inf.get("成员", "-"), r["facet"]))
    print("      导语：%s" % r["ld"].replace("\n", " "))


print("== 势力页检查 ==")
for nm in ["蝴蝶帮", "孤云山派", "孤云山", "养龙苑", "金国", "华山派", "全真派", "唐门"]:
    show(nm)

print("\n== 王二壮 ==")
r = c.execute("select name,title,lead from pages where type='人物' and name='丐帮·王二壮'").fetchone()
print("  ", r["name"], "称号", r["title"])
print("   ", (r["lead"] or "")[-90:])

print("\n== 唐门页 章节 ==")
secs = json.loads(c.execute("select sections from pages where type='势力' and name='唐门'").fetchone()["sections"])
for s in secs:
    h = s.get("h") or ""
    if h in ("上级势力", "下辖势力（1 个）", "本派成员（6 人）") or h.startswith(("下辖势力", "本派成员", "上级势力")):
        print("   【%s】 %d 行" % (h, len(s.get("rows") or [])))
        for rw in (s.get("rows") or [])[:4]:
            print("      -", rw.get("note", "")[:50])
print("\n== 势力页总数 ==", c.execute("select count(*) from pages where type='势力'").fetchone()[0])
