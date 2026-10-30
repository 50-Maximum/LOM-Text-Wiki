# -*- coding: utf-8 -*-
"""把台账汇总成实体，并用 LLM 合成条目简介。
用法: python build_entities.py <api_key>
"""
import sqlite3, os, sys, json, re, time, io, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
URL = "https://api.deepseek.com/chat/completions"
KEY = sys.argv[1] if len(sys.argv) > 1 else ""
AUTH = "Bea" + "rer " + KEY

ORDER = {"序章": 0, "第0章": 1, "第1章": 2}

def chap_key(ch):
    ch = ch.strip()
    if ch in ORDER:
        return (ORDER[ch], 0)
    m = re.match(r"第(\d+)章", ch)
    if m:
        n = int(m.group(1))
        p = re.search(r"·(\d+)$", ch)
        return (10 + n, int(p.group(1)) if p else 0)
    if ch.startswith("支线"):
        p = re.search(r"·(\d+)$", ch)
        return (100, int(p.group(1)) if p else 0)
    if ch == "角色线":
        return (200, 0)
    if ch.startswith("其他"):
        p = re.search(r"·(\d+)$", ch)
        return (300, int(p.group(1)) if p else 0)
    return (400, 0)

SYS = """你是《活侠传》wiki 的编辑。根据同一实体的多条剧情笔记，写一段客观介绍。
只输出 JSON：{"intro":"...","aliases":["..."],"tags":["..."]}
要求：
1. intro 3~6 句、120~260 字，按剧情时间先后组织，写清身份、归属、关键事迹、结局或现状。
2. 不写「本文」「本条目」之类套话，不写剧透警告，直接叙述。
3. 笔记之间有矛盾时按后出现的章节为准，或写成「一说…」。
4. aliases 只填原文中确实出现过的别称/称号，没有就空数组。
5. tags 2~4 个，如「唐门」「外姓弟子」「暗器」。"""

c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")
c.execute("""CREATE TABLE IF NOT EXISTS entities(
  type TEXT, name TEXT, intro TEXT, aliases TEXT, tags TEXT,
  mentions INTEGER, chapters TEXT, first_chapter TEXT,
  PRIMARY KEY(type,name))""")
c.execute("delete from entities")

groups = {}
for typ, name, ch, note, ev in c.execute(
        "select type,name,chapter,note,evidence from ledger order by rowid"):
    groups.setdefault((typ, name), []).append((ch, note, ev))

def collect(rows):
    seen, out = set(), []
    for ch, note, ev in rows:
        k = note.strip()
        if k in seen:
            continue
        seen.add(k)
        out.append((ch, note.strip(), ev.strip()))
    out.sort(key=lambda x: chap_key(x[0]))
    return out

def synth(typ, name, items):
    body = "\n".join(f"[{ch}] {note}" for ch, note, _ in items)
    prompt = f"实体类型：{typ}\n名称：{name}\n笔记：\n{body}"
    req = urllib.request.Request(URL, data=json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": prompt}],
        "temperature": 0.3, "max_tokens": 1200,
        "response_format": {"type": "json_object"},
    }).encode("utf-8"), headers={"Authorization": AUTH, "Content-Type": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read().decode("utf-8"))
            obj = json.loads(d["choices"][0]["message"]["content"])
            return obj.get("intro", "").strip(), obj.get("aliases", []), obj.get("tags", [])
        except Exception as e:
            if i == 2:
                return "", [], []
            time.sleep(2 * (i + 1))
    return "", [], []

todo = []
for (typ, name), rows in groups.items():
    items = collect(rows)
    chs = sorted({ch for ch, _, _ in items}, key=chap_key)
    c.execute("insert or replace into entities(type,name,intro,aliases,tags,mentions,chapters,first_chapter) "
              "values(?,?,?,?,?,?,?,?)",
              (typ, name, "", "[]", "[]", len(items),
               json.dumps(chs, ensure_ascii=False), chs[0] if chs else ""))
    if len(items) >= 3:
        todo.append((typ, name, items))

c.commit()
print("实体", len(groups), "需合成", len(todo), flush=True)

done = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(synth, t, n, it): (t, n) for t, n, it in todo}
    for fu in as_completed(futs):
        t, n = futs[fu]
        intro, aliases, tags = fu.result()
        c.execute("update entities set intro=?,aliases=?,tags=? where type=? and name=?",
                  (intro, json.dumps(aliases, ensure_ascii=False),
                   json.dumps(tags, ensure_ascii=False), t, n))
        done += 1
        if done % 20 == 0:
            c.commit()
            print(f"  {done}/{len(todo)}", flush=True)
c.commit()
ok = c.execute("select count(*) from entities where intro<>''").fetchone()[0]
print("完成，有简介", ok, "条")
