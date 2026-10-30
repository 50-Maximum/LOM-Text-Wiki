# -*- coding: utf-8 -*-
"""找本地化 CSV：扫全部 TextAsset，看哪些像「键,文本」表（含中文且行内有分隔符）。"""
import io, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
FILES = [f for f in os.listdir(GAME) if f.endswith(".assets")]
CJK = re.compile(r"[\u4e00-\u9fff]")

rows = []
for f in FILES:
    p = os.path.join(GAME, f)
    try:
        env = UnityPy.load(p)
    except Exception:
        continue
    for o in env.objects:
        if o.type.name != "TextAsset":
            continue
        try:
            d = o.read()
            nm = getattr(d, "m_Name", "") or ""
            s = d.m_Script
            if isinstance(s, bytes):
                s = s.decode("utf-8", "ignore")
        except Exception:
            continue
        if not s or len(s) < 200:
            continue
        lines = s.splitlines()
        sep = sum(1 for ln in lines[:400] if ("," in ln or "\t" in ln))
        zh = len(CJK.findall(s[:20000]))
        if zh > 200 and sep > len(lines[:400]) * 0.5:
            rows.append((zh, len(lines), nm, f, lines[0][:60], lines[1][:60] if len(lines) > 1 else ""))

rows.sort(reverse=True)
print("像键值表的 TextAsset", len(rows))
for zh, n, nm, f, h1, h2 in rows[:12]:
    print("\n%-26s 行 %-6d 中文 %-6d %s" % (nm, n, zh, f))
    print("   首行:", h1)
    print("   次行:", h2)
