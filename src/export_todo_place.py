# -*- coding: utf-8 -*-
"""导出待定地点清单：只取「有场景页但没有地点」的场次（与 wiki 里显示一致）。"""
import io, json, os, shutil, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
BG = json.load(open(os.path.join(BASE, "data", "scene_bg.json"), encoding="utf-8"))

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute(
    "select script,chapter,title,line_count from scenes")}

todo = []
for r in con.execute("select slug,sections from pages where type='场景'"):
    sc = r["slug"].split("/", 1)[1]
    txt = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
    if "地点：" in txt:
        continue
    todo.append(sc)

body = {}
for r in con.execute("select script,seq,text from lines order by script,seq"):
    if r["script"] not in scenes:
        continue
    t = (r["text"] or "").replace("\n", " ").strip()
    if len(t) < 6:
        continue
    body.setdefault(r["script"], [])
    if len(body[r["script"]]) < 2:
        body[r["script"]].append(t[:56])

CH_ORDER = ["序章", "第一章", "第二章", "第三章", "第四章", "第五章",
            "第六章", "第七章", "第八章", "第九章", "终章", "支线", "角色线", "其他"]


def chkey(ch):
    ch = ch or "其他"
    for i, x in enumerate(CH_ORDER):
        if ch.startswith(x):
            return (i, ch)
    return (len(CH_ORDER), ch)


groups = {}
for sc in todo:
    groups.setdefault(chkey(scenes.get(sc, {}).get("chapter")), []).append(sc)

lines = []
n = 0
lines.append("待定地点清单（共 %d 场）" % len(todo))
lines.append("")
lines.append("回复格式：编号 + 地点　例：001 唐门　　002 崆峒-铁拳巷　　003 不标")
lines.append("不确定的写「跳过」，我会继续留着。")
for k in sorted(groups):
    chs = sorted(groups[k])
    lines.append("")
    lines.append("-" * 58)
    lines.append("%s（%d 场）" % (k[1], len(chs)))
    lines.append("-" * 58)
    for sc in chs:
        n += 1
        d = scenes.get(sc, {})
        bgs = "、".join(BG.get(sc, [])[:2])
        meta = []
        if d.get("title"):
            meta.append("标题：%s" % d["title"])
        meta.append("%d 句" % (d.get("line_count") or 0))
        if bgs:
            meta.append("背景：%s" % bgs)
        lines.append("")
        lines.append("%03d  %s" % (n, sc))
        lines.append("     " + " ｜ ".join(meta))
        for t in body.get(sc, [])[:2]:
            lines.append("     > " + t)

txt = "\n".join(lines)
p = os.path.join(BASE, "data", "待定地点清单.txt")
open(p, "w", encoding="utf-8").write(txt)
shutil.copy(p, r"C:\Users\Luo\Desktop\待定地点清单.txt")
print("共 %d 场 → %s（已复制桌面）" % (len(todo), p))
for k in sorted(groups):
    print("   %-8s %d" % (k[1], len(groups[k])))
