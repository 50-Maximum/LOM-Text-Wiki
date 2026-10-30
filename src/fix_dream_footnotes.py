# -*- coding: utf-8 -*-
"""把「引用了梦境场景、却没标明是梦」的脚注补上标注。"""
import io, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
dream = json.load(open(B + r"\dream_scenes.json", encoding="utf-8"))
P = B + r"\intros_char.json"
d = json.load(open(P, encoding="utf-8"))

MARK = "（出自梦境，非现实）"
n = 0
for slug, v in d.items():
    for fn in (v.get("footnotes") or []):
        if fn.get("script") not in dream:
            continue
        tx = fn.get("text") or ""
        if ("梦" in tx) or ("幻" in tx) or (MARK in tx):
            continue
        fn["text"] = tx + MARK
        n += 1
        print("  %-16s 脚注%s ｜ %s" % (slug, fn.get("n"), tx[:34]))

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("补标 %d 条" % n)
