# -*- coding: utf-8 -*-
"""收尾：删两个占位掌门页、修阿叔简介、补齐剩余模板话术。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


cf = load("chars_fix.json")
dl = cf.setdefault("delete", [])
for x in ["铁拳门·掌门", "玄功门·掌门"]:
    if x not in dl:
        dl.append(x)
save("chars_fix.json", cf)
print("删除占位页：铁拳门·掌门、玄功门·掌门")

ic = load("intros_char.json")
print("含阿叔的导语键：", [k for k in ic if "阿叔" in k])
txt = ("樊啸天的阿叔，丐帮旧派的人。他认定现任帮主是假乞丐，自己那一群才是真正的丐帮；"
       "樊啸天因此跟着他敌视帮主。")
for k in [k for k in ic if "阿叔" in k]:
    node = ic[k]
    if isinstance(node, dict):
        node["text"] = txt
    else:
        ic[k] = {"text": txt, "footnotes": []}
save("intros_char.json", ic)

# 剩余模板话术
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
left = [r["name"] for r in c.execute("select name from pages where type='人物' and lead like '%原文中出现%'")]
print("仍用模板话术：", left)
