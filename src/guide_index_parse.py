# -*- coding: utf-8 -*-
"""解析全事件索引：章节段 + 年月旬 + 事件名 + 游戏脚本 → guide_index 表。"""
import os, re, io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
GUIDE = r"D:\LegendOfMortal Wiki\data\guide"
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
path = os.path.join(GUIDE, "全事件索引.txt")
lines = open(path, encoding="utf-8").read().split("\n")

RX_SEC = re.compile(r"^##\s*(.+)")
RX_YM = re.compile(r"^\|\s*(\d)年\s*\|\s*(\d{1,2})月\s*\|(.*)$")
RX_DET = re.compile(r"^\|\s*📌\s*([^触]+?)触发(.*)$")
RX_SCRIPT = re.compile(r"([A-Za-z0-9_]+(?:\.txt)?)")
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
      "十一": 11, "十二": 12}

sec = ""; year = None; month = None
cells = []  # 上/中/下 三个单元的事件名串
rows = []
pending = []  # 当前时间行的事件名列表

def split_cells(rest):
    parts = [p.strip() for p in rest.strip().strip("|").split("|")]
    return parts

for ln in lines:
    s = ln.rstrip()
    m = RX_SEC.match(s)
    if m:
        sec = m.group(1).strip()
        continue
    m = RX_YM.match(s)
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        cells = split_cells(m.group(3))
        continue
    m = RX_DET.match(s)
    if m:
        name = m.group(1).strip()
        body = s
        scripts = sorted(set(re.findall(r"游戏脚本[:：]\s*([^\s|]+)", body)))
        sch = []
        for x in scripts:
            for y in re.split(r"[、,，/]", x):
                y = y.strip()
                if not y:
                    continue
                if not y.endswith(".txt"):
                    y += ".txt"
                sch.append(y[:-4])
        xun = ""
        if cells:
            for i, c in enumerate(cells[:3]):
                if name and name in c:
                    xun = ["上旬", "中旬", "下旬"][i]
                    break
        rows.append({"sec": sec, "year": year, "month": month, "xun": xun,
                     "name": name, "scripts": ",".join(sch), "body": body})
        continue

print("解析事件", len(rows))
c = sqlite3.connect(DB)
c.execute("drop table if exists guide_index")
c.execute("""create table guide_index(
    id integer primary key, sec text, year integer, month integer, xun text,
    name text, scripts text, body text)""")
c.executemany("insert into guide_index(sec,year,month,xun,name,scripts,body) values(?,?,?,?,?,?,?)",
              [(r["sec"], r["year"], r["month"], r["xun"], r["name"], r["scripts"], r["body"]) for r in rows])
c.commit()

print("\n脚本覆盖检查：")
n_hit = 0; n_tot = 0
for r in rows:
    for sc in (r["scripts"] or "").split(","):
        if not sc:
            continue
        n_tot += 1
        if c.execute("select 1 from scenes where script=?", (sc,)).fetchone():
            n_hit += 1
print(f"脚本引用 {n_tot} 个，能对上 wiki 场景 {n_hit} 个")

print("\n样本：")
for r in rows[:6]:
    print(r["year"], r["month"], r["xun"], r["name"], "|", r["scripts"])
