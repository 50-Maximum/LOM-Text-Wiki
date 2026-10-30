# -*- coding: utf-8 -*-
import sys, os, json, io, sqlite3
sys.path.insert(0, r"D:\LegendOfMortal Wiki\src")
import importlib
m = importlib.import_module("build_intros_all")
todo = m.collect()
typ, name = "人物", "邹博"
c = sqlite3.connect(m.DB)
for t, n, rows in todo:
    if t == typ and n == name:
        block = f"条目：{typ}「{name}」\n以下是从各场景抽取的笔记（含逐字引文）：\n"
        for sc, a, note, q in rows[:45]:
            block += f"- {sc}#{a} {note} | {q}\n"
        print(block[:2800])
        r = m.call("deepseek-chat", block)
        print("===== 响应 =====")
        print(json.dumps(r, ensure_ascii=False, indent=1)[:2800])
        break
