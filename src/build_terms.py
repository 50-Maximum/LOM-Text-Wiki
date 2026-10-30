# -*- coding: utf-8 -*-
"""从全文建「名词索引」：势力、地点、书名。严格过滤，避免把掌门/参见之类收进来。"""
import sqlite3, re, collections, json

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
texts = [r["text"] for r in c.execute("SELECT text FROM lines WHERE text<>''")]

BAD_WORDS = ("掌门", "帮主", "楼主", "阁主", "教主", "宫主", "庄主", "谷主",
             "公子", "姑娘", "先生", "前辈", "大侠", "女侠", "少侠", "弟子",
             "门派", "武林", "江湖", "众人", "我们", "你们", "他们", "咱们")
BAD_PREFIX = ("参见", "拜见", "多谢", "见过", "告诉", "请问", "请教", "邀请", "迎接",
              "拜访", "求见", "启禀", "在下", "阁下", "诸位", "各位", "如今", "现在",
              "当时", "后来", "于是", "但是", "如果", "虽然", "因为", "所以", "而且",
              "并且", "不过", "只是", "还是", "就是", "不是", "也是", "都是", "便是",
              "可是", "这个", "那个", "哪个", "什么", "怎么", "为何", "为了", "对于",
              "关于", "由于", "至于", "甚至", "已经", "曾经", "将要", "正在", "立刻",
              "马上", "一起", "一同", "大家", "有人", "没人", "此人", "那人")
BAD_FIRST = set("的了在是与和跟对把被让给向从往到于为以及或而则即便却又还都很快太更最不没有会能要想说道问答笑看听走来去回出进上下这那哪什么怎我你他她它您咱")

FAC_SUF = ["世家", "派", "门", "楼", "阁", "教", "帮", "宫", "庄", "谷", "寨", "岛", "寺", "观", "宗", "盟", "会"]
PLACE_SUF = ["殿", "堂", "院", "楼", "阁", "山", "谷", "庄", "寨", "岛", "城", "寺", "观",
             "洞", "峰", "林", "镇", "坊", "市", "街", "巷", "关", "渡", "陵", "池", "泉",
             "塔", "桥", "园", "居", "轩", "斋"]

def ok(name):
    if len(name) < 3 or len(name) > 8:
        return False
    if any(x in name for x in BAD_WORDS):
        return False
    if name.startswith(BAD_PREFIX):
        return False
    if name[0] in BAD_FIRST:
        return False
    return True

def mine(suffixes, minn=4):
    pat = re.compile(r"([\u4e00-\u9fff]{2,5})(" + "|".join(suffixes) + r")")
    cnt = collections.Counter()
    for t in texts:
        for m in pat.finditer(t):
            n = m.group(1) + m.group(2)
            if ok(n):
                cnt[n] += 1
    return [(k, v) for k, v in cnt.items() if v >= minn]

facs = mine(FAC_SUF, 4)
places = mine(PLACE_SUF, 4)
books = collections.Counter(m.group(1) for t in texts for m in re.finditer(r"《([^》]{2,14})》", t))
books = [(k, v) for k, v in books.items() if v >= 2]

c.execute("DROP TABLE IF EXISTS terms")
c.execute("CREATE TABLE terms(type TEXT, name TEXT, n INT, PRIMARY KEY(type,name))")
rows = [("势力", n, k) for n, k in facs] + [("地点", n, k) for n, k in places] + [("书名", n, k) for n, k in books]
c.executemany("INSERT OR REPLACE INTO terms VALUES(?,?,?)", rows)
c.commit()

for label, items in (("势力", facs), ("地点", places), ("书名", books)):
    items = sorted(items, key=lambda x: -x[1])
    print(label, len(items))
    for n, k in items[:30]:
        print(f"  {k:4d} {n}")
json.dump({"势力": sorted(facs, key=lambda x: -x[1])[:120],
           "地点": sorted(places, key=lambda x: -x[1])[:160],
           "书名": sorted(books, key=lambda x: -x[1])[:120]},
          open(r"D:\LegendOfMortal Wiki\data\summary\名词索引.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
