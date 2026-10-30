# -*- coding: utf-8 -*-
"""从全文挖地点、人物称谓、书名/功法候选。"""
import sqlite3, re, collections, json

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
OUT = r"D:\LegendOfMortal Wiki\data\summary"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row

texts = [r["text"] for r in c.execute("SELECT text FROM lines WHERE text<>''")]

PLACE_SUF = "殿堂院楼阁山谷庄寨岛城寺观洞峰林镇坊市街巷关渡陵池泉塔桥门园居轩斋"
place_pat = re.compile(r"([\u4e00-\u9fff]{2,5})([" + PLACE_SUF + r"])")
STOP = set("这个 那个 一个 一门 这门 那门 你们 我们 他们 咱们 什么 怎么 如此 这般 大门 后山 上山 下山 山中 山上 山下 门口 门人 弟子 门派 帮派 教派 江湖 这里 那里 哪里 进来 出来 回来 起来 出来".split())

pc = collections.Counter()
for t in texts:
    for m in place_pat.finditer(t):
        n = m.group(1) + m.group(2)
        if len(n) < 3 or m.group(1) in STOP:
            continue
        if any(x in m.group(1) for x in ("这", "那", "哪", "什", "怎", "我", "你", "他", "她", "不", "没")):
            continue
        pc[n] += 1

per_pat = re.compile(r"([\u4e00-\u9fff]{2,3})(掌门|帮主|楼主|阁主|教主|宫主|庄主|谷主|公子|姑娘|先生|前辈|大侠|女侠|少侠)")
pcn = collections.Counter()
for t in texts:
    for m in per_pat.finditer(t):
        pcn[m.group(1) + m.group(2)] += 1

book_pat = re.compile(r"《([^》]{2,12})》")
bc = collections.Counter()
for t in texts:
    for m in book_pat.finditer(t):
        bc[m.group(1)] += 1

def dump(name, counter, limit=80, minn=3):
    items = [(k, v) for k, v in counter.items() if v >= minn]
    items.sort(key=lambda x: -x[1])
    json.dump(items, open(OUT + "\\" + name, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(name, len(items))
    for k, v in items[:limit]:
        print(f"  {v:4d} {k}")
    return items

print("=== 地点候选 ===")
dump("地点候选.json", pc, 60, 3)
print("=== 人物称谓候选 ===")
dump("人物称谓候选.json", pcn, 60, 2)
print("=== 书名/功法候选 ===")
dump("书名候选.json", bc, 60, 1)
