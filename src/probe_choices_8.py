# -*- coding: utf-8 -*-
"""choices.options 是 JSON 数组，在 Python 侧匹配年表选项指纹。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

rows = list(c.execute("select script,seq,checkpoint,options from choices"))
print("choices 行数 %d" % len(rows))
print("样例 options:", (rows[0][3] or "")[:200] if rows else "-")

PROBES = {
    "你，听过唐门吗？/初识唐升": ["附和三师兄", "干话刺激他", "好听的话安慰他"],
    "招募弟子结果": ["没招到人", "抢走零用钱"],
    "照镜子": ["还不算差", "内在更重要", "实在是难看"],
    "惊吓指数": ["讲干话对付他"],
    "初识唐布衣": ["穿体面点", "好像懂"],
    "初识唐铮": ["来找工作的吗", "来找死的吗"],
    "四书事件(一)同门霸凌": ["老子跟你们拼了"],
    "四书事件(二)蒙面人前辈": ["非得亲手了断", "试试再告状"],
}
for label, ps in PROBES.items():
    print("\n=== " + label)
    for p in ps:
        hit = []
        for sc, seq, ck, opt in rows:
            if opt and p in opt:
                hit.append((sc, seq, ck))
        for sc, seq, ck in hit[:3]:
            print("   OK  %-26s seq%-5s ck=%s" % (sc, seq, ck))
        if not hit:
            print("   --  %s 未命中" % p)
