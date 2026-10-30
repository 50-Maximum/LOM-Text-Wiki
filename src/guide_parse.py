# -*- coding: utf-8 -*-
"""解析攻略文本为结构化事件库：name/time(year,month,xun)/place/cond/body/source。"""
import os, re, io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
GUIDE = r"D:\LegendOfMortal Wiki\data\guide"
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"

CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
      "十一": 11, "十二": 12}
RX_TIME = re.compile(r"触发时间[:：]\s*([^\n|]*)")
RX_YEAR = re.compile(r"第([一二三四])年")
RX_MONTH = re.compile(r"([一二三四五六七八九十]{1,3})月")
RX_XUN = re.compile(r"(上旬|中旬|下旬)")
RX_PLACE = re.compile(r"地点[:：]\s*([^\n|]*)")
RX_COND = re.compile(r"条件[:：]\s*([^\n|]*)")

def norm_time(t):
    t = (t or "").strip()
    y = None; m = None; x = None
    ym = RX_YEAR.search(t)
    if ym:
        y = CN.get(ym.group(1))
    mm = RX_MONTH.search(t)
    if mm:
        m = CN.get(mm.group(1))
    xm = RX_XUN.search(t)
    if xm:
        x = xm.group(1)
    return y, m, x

def parse_file(path, source):
    out = []
    lines = open(path, encoding="utf-8").read().split("\n")
    cur = None
    for ln in lines:
        s = ln.strip()
        if s.startswith("|"):
            if "触发时间：" in s or "触发时间:" in s:
                if cur:
                    out.append(cur)
                parts = s.strip("|").split("|")
                head = parts[0].strip()
                name = head.split("触发时间")[0].strip()
                rest = "|".join(parts[1:])
                tm = RX_TIME.search(s)
                y, m, x = norm_time(tm.group(1) if tm else "")
                pl = RX_PLACE.search(s)
                cd = RX_COND.search(s)
                body = s
                cur = {"name": name, "year": y, "month": m, "xun": x,
                       "place": (pl.group(1).strip() if pl else ""),
                       "cond": (cd.group(1).strip() if cd else ""),
                       "body": body, "source": source}
            elif cur:
                cur["body"] += "\n" + s
        elif s.startswith("####"):
            if cur:
                out.append(cur); cur = None
        elif s.startswith("#"):
            if cur:
                out.append(cur); cur = None
    if cur:
        out.append(cur)
    return out

all_ev = []
for fn in ("主线攻略.txt", "一次性事件.txt", "重复性事件.txt", "特殊事件.txt", "全事件索引.txt"):
    p = os.path.join(GUIDE, fn)
    if os.path.exists(p):
        ev = parse_file(p, fn)
        print(fn, len(ev), "条")
        all_ev.extend(ev)

# 去重（同名同时间）
seen = set(); uniq = []
for e in all_ev:
    k = (e["name"], e["year"], e["month"], e["xun"])
    if k in seen:
        continue
    seen.add(k); uniq.append(e)

json.dump(uniq, open(os.path.join(GUIDE, "events.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

c = sqlite3.connect(DB)
c.execute("drop table if exists guide_events")
c.execute("""create table guide_events(
    id integer primary key, name text, year integer, month integer, xun text,
    place text, cond text, body text, source text)""")
c.executemany("insert into guide_events(name,year,month,xun,place,cond,body,source) values(?,?,?,?,?,?,?,?)",
              [(e["name"], e["year"], e["month"], e["xun"], e["place"], e["cond"], e["body"], e["source"]) for e in uniq])
c.commit()
print("写入 guide_events", len(uniq), "条")

# 打印时间分布
for r in c.execute("""select year,month,count(*) from guide_events
                      group by year,month order by year,month"""):
    print(r)
