# -*- coding: utf-8 -*-
"""给地图事件补时间窗：从条件里抽「目前時間 ≥ / ≤ 第X年X月X旬」。

写回 data/position_events.json 的 start/end/start_key/end_key 字段。
"""
import io, sys, json, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
P = WIKI + r"\data\position_events.json"

NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
       "十一": 11, "十二": 12}
XUN = {"上": 1, "中": 2, "下": 3}
PAT = re.compile(r"第([一二三四])年([一二三四五六七八九十]{1,3})月([上中下])旬")


def parse(t):
    m = PAT.search(t or "")
    if not m:
        return None
    y = NUM.get(m.group(1))
    mo = NUM.get(m.group(2))
    x = XUN.get(m.group(3))
    if not (y and mo and x):
        return None
    return y, mo, x, "%d年%d月%s旬" % (y, mo, m.group(3)), y * 1000 + mo * 10 + x


def main():
    data = json.load(open(P, encoding="utf-8"))
    n0 = n1 = 0
    for d in data:
        s = e = None
        pool = list(d.get("cond") or [])
        for r in d.get("rates") or []:
            pool += list(r.get("cond") or [])
        for c in pool:
            if "目前時間" not in c and "目前时间" not in c:
                continue
            p = parse(c)
            if not p:
                continue
            if "≥" in c and not s:
                s = p
            elif "≤" in c and not e:
                e = p
        if s:
            d["start"], d["start_key"] = s[3], s[4]
        if e:
            d["end"], d["end_key"] = e[3], e[4]
        n0 += 1 if s else 0
        n1 += 1 if e else 0
    json.dump(data, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("有起始时间:", n0, " 有结束时间:", n1, " 总:", len(data))
    for d in [x for x in data if x.get("start")][:8]:
        print("   %-26s %s ～ %s" % (d["name"], d.get("start"), d.get("end", "不限")))


if __name__ == "__main__":
    main()
