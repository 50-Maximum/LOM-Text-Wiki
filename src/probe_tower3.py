# -*- coding: utf-8 -*-
"""练功塔一串 act* 剧本的完整链路、外部入口、以及攻略/参考 wiki 是否有记录。"""
import io, sys, json, sqlite3, re, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

print("=== guide_events 列名")
print([d[1] for d in c.execute("pragma table_info(guide_events)")])
print("=== scene_order / scene_time 列名")
print([d[1] for d in c.execute("pragma table_info(scene_order)")])

# 所有 act* 剧本
acts = [r[0] for r in c.execute("select script from scenes where script like 'act%' order by script")]
print("\n=== act* 剧本 %d 个" % len(acts))
RAW = os.path.join(B, "data", "raw", "scripts")
refs = {}
for f in glob.glob(os.path.join(RAW, "*.txt")):
    sc = os.path.basename(f)[:-4]
    try:
        txt = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for a in acts:
        if ('"%s"' % a) in txt or ("+" + a + "+") in txt:
            refs.setdefault(a, set()).add(sc)

for a in acts:
    t = c.execute("select title,chapter,line_count from scenes where script=?", (a,)).fetchone()
    src = sorted(refs.get(a) or [])
    print("  %-12s %-14s 句%3d ← %s" % (a, (t[0] or "")[:12], t[2] or 0,
                                        ", ".join(src) if src else "（无引用）"))

print("\n=== act* 是否在 scene_order / scene_time / 剧情段")
for a in acts:
    o = c.execute("select count(*) from scene_order where script=?", (a,)).fetchone()[0]
    tm = c.execute("select count(*) from scene_time where script=?", (a,)).fetchone()[0]
    print("  %-12s order=%d time=%d" % (a, o, tm))

print("\n=== 参考 wiki 里搜「练功塔」")
REF = r"C:\Users\Luo\Downloads\LoM-wiki-1.7.0\LoM-wiki-1.7.0"
hits = 0
for f in glob.glob(os.path.join(REF, "**", "*.md"), recursive=True):
    try:
        s = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    if "练功塔" in s or "練功塔" in s:
        hits += 1
        print("  ", os.path.relpath(f, REF))
        for ln in s.split("\n"):
            if "练功塔" in ln or "練功塔" in ln:
                print("      ", ln.strip()[:100])
                break
print(" 命中文件", hits)
