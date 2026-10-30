# -*- coding: utf-8 -*-
"""给没有官方名的事件起中文事件名。"""
import sqlite3, os, sys, json, time, io, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
URL = "https://api.deepseek.com/chat/completions"
KEYFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "key.txt")
KEY = open(KEYFILE, encoding="utf-8").read().strip()
AUTH = "Bea" + "rer " + KEY

SYS = """你是《活侠传》wiki 的编辑，为剧情场景起事件名。
只输出 JSON：{"items":[{"script":"脚本名","title":"事件名"}]}
要求：
1. 事件名 4~12 个汉字，不用书名号引号，不加地点前缀。
2. 写成能看懂的事件：谁做了什么、发生了什么。如「赵活夜探外堡」「唐门招亲生变」「谭霸刀当众认罪」。
3. 有对决就点明，如「与金乌上人决战」。
4. 避免「对话」「交谈」「日常」这类空名；信息不足时用最有特征的一句概括。
5. 同一批里不要重名。"""


def first_lines(script, n=8):
    conn = sqlite3.connect(DB)
    try:
        rows = conn.execute(
            "select speaker,text from lines where script=? and text<>'' order by seq limit ?",
            (script, n)).fetchall()
    finally:
        conn.close()
    out = []
    for sp, tx in rows:
        tx = tx.replace("\n", " ")[:70]
        out.append(f"{sp}：{tx}" if sp and sp != "旁白" else f"旁白：{tx}")
    return "\n".join(out)


def call(user):
    body = json.dumps({"model": "deepseek-chat",
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": user}],
                       "temperature": 0.4, "max_tokens": 1200,
                       "response_format": {"type": "json_object"}}).encode("utf-8")
    req = urllib.request.Request(URL, data=body,
                                 headers={"Authorization": AUTH,
                                          "Content-Type": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read().decode("utf-8"))
            return json.loads(d["choices"][0]["message"]["content"]).get("items", [])
        except Exception:
            if i == 2:
                return []
            time.sleep(2 * (i + 1))
    return []


conn = sqlite3.connect(DB)
scenes = conn.execute("""select script,chapter,place,line_count from scenes
                         where (title_src is null or title_src in ('weak','derived'))
                           and line_count>0 order by line_count desc""").fetchall()
conn.close()
print("待命名", len(scenes), flush=True)

conn = sqlite3.connect(DB)
conn.execute("PRAGMA journal_mode=WAL")
updated = 0
step = 6
lock = __import__("threading").Lock()

def work(chunk):
    block = "\n\n".join(
        f"脚本：{s}\n章节：{ch}　地点：{pl or '未注明'}　{sent}句\n{first_lines(s)}"
        for s, ch, pl, sent in chunk)
    return chunk, call(block)

with ThreadPoolExecutor(max_workers=4) as ex:
    futs = [ex.submit(work, scenes[i:i + step]) for i in range(0, len(scenes), step)]
    for fu in as_completed(futs):
        chunk, items = fu.result()
        for it in items:
            sc, title = it.get("script", ""), (it.get("title") or "").strip()
            if not sc or not title or len(title) < 3:
                continue
            if not any(c[0] == sc for c in chunk):
                continue
            conn.execute("update scenes set title=?, title_src='llm' where script=?", (title, sc))
            updated += 1
        conn.commit()
        print("  ", updated, "/", len(scenes), flush=True)

conn.commit()
print("命名完成", updated)
