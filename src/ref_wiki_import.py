# -*- coding: utf-8 -*-
"""把下载的繁中 wiki 转成简中并抽成结构化数据，便于比对。
输出 data/ref_wiki/characters.json、timeline.json、events.json
"""
import io, os, re, sys, json, glob
from opencc import OpenCC

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CC = OpenCC("t2s")
SRC = r"C:\Users\Luo\Downloads\LoM-wiki-1.7.0\LoM-wiki-1.7.0\docs"
OUT = r"D:\LegendOfMortal Wiki\data\ref_wiki"
os.makedirs(OUT, exist_ok=True)


def s(x):
    return CC.convert(x or "").strip()


# ---------- 人物 ----------
chars = []
for p in glob.glob(os.path.join(SRC, "people", "characters", "*.md")):
    t = open(p, encoding="utf-8", errors="replace").read()
    if not t.startswith("---"):
        continue
    head, _, body = t[3:].partition("\n---")
    title = re.search(r"^title:\s*(.+)$", head, re.M)
    tags = re.findall(r"^\s{4}-\s*(.+)$", head, re.M)
    ntitle = re.search(r"nameTitle='([^']*?)'", body)
    nmain = re.search(r"nameMain='([^']*?)'", body)
    info = {}
    for tr in re.findall(r"<ChTr>(.*?)</ChTr>", body, re.S):
        tds = re.findall(r"<ChTd[^>]*>(.*?)</ChTd>", tr, re.S)
        if len(tds) < 2:
            continue
        k = s(re.sub(r"<[^>]+>", "", tds[0])).strip()
        v = s(re.sub(r"<[^>]+>", " ", tds[1]))
        v = re.sub(r"\s+", " ", v).strip()
        if k and v:
            info.setdefault(k, v)
    chars.append({
        "key": os.path.basename(p)[:-3],
        "title": s(title.group(1)) if title else "",
        "name": s(nmain.group(1)) if nmain else "",
        "chtitle": s(ntitle.group(1)) if ntitle else "",
        "tags": [s(x) for x in tags],
        "info": info,
    })
json.dump(chars, open(os.path.join(OUT, "characters.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("人物 %d 个，有称号 %d，有门派标签 %d"
      % (len(chars), sum(1 for c in chars if c["chtitle"]),
         sum(1 for c in chars if len(c["tags"]) > 1)))

# ---------- 主支线年表 ----------
tl = []
p = os.path.join(SRC, "event", "story-branch-timeline.md")
if os.path.exists(p):
    t = open(p, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"<tr>(.*?)</tr>", t, re.S):
        cells = [s(re.sub(r"<[^>]+>", " ", c)).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(1), re.S)]
        cells = [re.sub(r"\s+", " ", c) for c in cells]
        if len(cells) >= 6 and cells[5]:
            tl.append({"kind": cells[0], "place": cells[1], "year": cells[2],
                       "month": cells[3], "xun": cells[4], "event": cells[5],
                       "cond": cells[6] if len(cells) > 6 else "",
                       "note": cells[7] if len(cells) > 7 else ""})
json.dump(tl, open(os.path.join(OUT, "timeline.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("年表 %d 行" % len(tl))
from collections import Counter
print("  类别:", Counter(x["kind"] for x in tl).most_common(6))

# ---------- 简易表格：年 / 月 / 旬 → 事件名 ----------
cal = []
p = os.path.join(SRC, "event", "story-simple-table.md")
if os.path.exists(p):
    t = open(p, encoding="utf-8", errors="replace").read()
    cur_year = ""
    for part in re.split(r"(?=<h2|## )", t):
        m = re.search(r"##\s*(第[一二三四五六七八九十]+年)", part)
        if m:
            cur_year = s(m.group(1))
        for tr in re.finditer(r"<tr>(.*?)</tr>", part, re.S):
            tds = re.findall(r"<td[^>]*>(.*?)</td>", tr.group(1), re.S)
            if len(tds) < 4:
                continue
            month = s(re.sub(r"<[^>]+>", "", tds[0])).strip()
            if not month or "月" not in month:
                continue
            for idx, xun in enumerate(("上", "中", "下"), start=1):
                cell = tds[idx]
                for name, link in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", cell):
                    cal.append({"year": cur_year, "month": month, "xun": xun,
                                "name": s(name), "link": link})
json.dump(cal, open(os.path.join(OUT, "calendar.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("简易年表 %d 条" % len(cal))
if cal:
    print("  首条:", cal[0])

evs = []
for p in glob.glob(os.path.join(SRC, "event", "**", "*.md"), recursive=True):
    t = open(p, encoding="utf-8", errors="replace").read()
    if not t.startswith("---"):
        continue
    head, _, body = t[3:].partition("\n---")
    title = re.search(r"^title:\s*(.+)$", head, re.M)
    tags = re.findall(r"^\s{4}-\s*(.+)$", head, re.M)
    evs.append({"file": os.path.relpath(p, SRC).replace("\\", "/"),
                "title": s(title.group(1)) if title else os.path.basename(p)[:-3],
                "tags": [s(x) for x in tags],
                "chars": len(body),
                "text": s(re.sub(r"<[^>]+>", "", body))[:400]})
json.dump(evs, open(os.path.join(OUT, "events.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("事件 md %d 篇" % len(evs))
print("样例人物:", chars[0]["title"], "|", chars[0]["chtitle"], "|", chars[0]["tags"])
print("样例年表:", tl[0] if tl else "无")
