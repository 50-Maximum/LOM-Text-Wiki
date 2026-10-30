# -*- coding: utf-8 -*-
"""按场景逐句抽取台账：note 只写本场，quote 必须逐字来自本场台词。

用法:
  python build_notes.py sample <script> [model]   # 单场试跑，打印
  python build_notes.py run [model]               # 全量写入 notes 表
"""
import os, sys, json, time, io, re, sqlite3, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
DB = os.path.join(BASE, "data", "wiki.db")
KF = os.path.join(BASE, "data", "key.txt")
KEY = ""
if os.path.exists(KF):
    fh = open(KF, "r", encoding="utf-8"); KEY = fh.read().strip(); fh.close()
URL = "https://api.deepseek.com/chat/completions"
AUTH = "Bea" + "rer " + KEY

SYS = """你是《活侠传》wiki 的编辑。读一场戏的台词，抽取值得立条目的实体。
只输出 JSON：{"entries":[{"type":"势力|地点|人物|关系|书物|事件","name":"...","note":"...","quote":"...","seq_from":12,"seq_to":13}]}
铁律：
1. note 只写这一场戏里实际发生的事，一句话，20~55 字。不得掺入其他场景的内容，不得写推测、评价或游戏机制说明。
2. quote 必须从台词里逐字复制（含标点），不超过 40 字，是 note 的直接依据。不得改写、拼接、省略号替换。
3. seq_from/seq_to 填 quote 所在句的序号；跨句时填首末句。
4. 只收有名字的：人物、势力、地点、有名目的物品/书、关系、本场事件。泛称（唐门弟子、路人、店小二）不收。
5. 事件条目写这一场的核心事件，name 用 8~16 字，如「易凡登门求娶唐默铃」。
6. 关系条目 name 写「A—B」，note 说明本场确认的关系。
7. 每场最多 10 条；宁缺勿滥。"""


def norm(s):
    return re.sub(r"\s+", "", s or "")


def fetch_lines(script):
    c = sqlite3.connect(DB)
    rows = c.execute("select seq,speaker,text from lines where script=? order by seq", (script,)).fetchall()
    c.close()
    return rows


def chunk_lines(rows, n=60, overlap=6):
    out, i = [], 0
    while i < len(rows):
        seg = rows[i:i + n]
        out.append(seg)
        if i + n >= len(rows):
            break
        i += n - overlap
    return out


def call(model, prompt):
    body = json.dumps({"model": model,
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": prompt}],
                       "temperature": 0.1, "max_tokens": 2200,
                       "response_format": {"type": "json_object"}}).encode("utf-8")
    req = urllib.request.Request(URL, data=body,
                                 headers={"Authorization": AUTH, "Content-Type": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.loads(r.read().decode("utf-8"))
            return json.loads(d["choices"][0]["message"]["content"]).get("entries", [])
        except Exception:
            if i == 2:
                return []
            time.sleep(2 * (i + 1))
    return []


def build_block(script, title, chapter, seg):
    head = f"场景：{script}《{title or script}》（{chapter}）\n"
    body = "\n".join(f"[{q}] {sp}：{(tx or '').replace(chr(10), ' ')}" for q, sp, tx in seg)
    return head + body


def validate(entries, seg):
    """quote 必须能在 seq 区间内逐字找到。"""
    ok, bad = [], []
    for e in entries:
        q = e.get("quote") or ""
        if not q:
            bad.append((e, "空引文")); continue
        a = int(e.get("seq_from") or 0); b = int(e.get("seq_to") or a)
        seg_map = {q0: tx for q0, sp, tx in seg}
        pool = ""
        for k in range(a, b + 1):
            if k in seg_map:
                pool += seg_map[k]
        if norm(q) and norm(q) in norm(pool):
            ok.append(e)
        else:
            bad.append((e, "引文不在指定句"))
    return ok, bad


def run_scene(script, model, title="", chapter="", save=False):
    rows = fetch_lines(script)
    if not rows:
        return 0, 0
    total_ok = total_bad = 0
    c = sqlite3.connect(DB) if save else None
    for seg in chunk_lines(rows):
        block = build_block(script, title, chapter, seg)
        entries = call(model, block)
        ok, bad = validate(entries, seg)
        # 校验失败的重试一次，明确告知可用句子
        if bad:
            retry_note = "\n\n上一轮这些条目的 quote 不在指定句里，请重做：\n" + \
                "\n".join(f"- {b[0].get('name')}：quote「{b[0].get('quote')}」{b[1]}" for b in bad[:6])
            entries2 = call(model, block + retry_note)
            ok2, bad2 = validate(entries2, seg)
            ok += [e for e in ok2 if all(e.get("quote") != x.get("quote") for x in ok)]
            total_bad += len(bad2)
        total_ok += len(ok)
        if save and ok:
            for e in ok:
                c.execute("""insert into notes(script,seq_from,seq_to,type,name,note,quote)
                             values(?,?,?,?,?,?,?)""",
                          (script, int(e.get("seq_from") or 0), int(e.get("seq_to") or 0),
                           e.get("type", ""), e.get("name", ""),
                           e.get("note", ""), e.get("quote", "")))
            c.commit()
    if c:
        c.close()
    return total_ok, total_bad


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sample"
    if mode == "sample":
        script = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else "deepseek-v4-pro"
        c = sqlite3.connect(DB)
        row = c.execute("select title,chapter from scenes where script=?", (script,)).fetchone()
        c.close()
        rows = fetch_lines(script)
        print(f"场景 {script} 共 {len(rows)} 句，模型 {model}")
        for seg in chunk_lines(rows):
            block = build_block(script, row[0] if row else "", row[1] if row else "", seg)
            ents = call(model, block)
            ok, bad = validate(ents, seg)
            for e in ok:
                print(f"   ✓ {e.get('type')}｜{e.get('name')}｜{e.get('note')}")
                print(f"      seq {e.get('seq_from')}-{e.get('seq_to')}：「{e.get('quote')}」")
            for e, why in bad:
                print(f"   ✗ {e.get('name')}｜{why}｜「{e.get('quote')}」")
    else:
        model = sys.argv[2] if len(sys.argv) > 2 else "deepseek-v4-pro"
        c = sqlite3.connect(DB)
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript("""drop table if exists notes;
            create table notes(script TEXT, seq_from INT, seq_to INT, type TEXT,
                               name TEXT, note TEXT, quote TEXT);
            create index idx_notes_ent on notes(type,name);
            create index idx_notes_script on notes(script);""")
        scenes = c.execute("select script,title,chapter,line_count from scenes where line_count>=3").fetchall()
        c.close()
        print("待处理场景", len(scenes), "模型", model)
        done = okn = badn = 0
        lock = __import__("threading").Lock()
        def work(sc):
            try:
                return sc[0], run_scene(sc[0], model, sc[1], sc[2], save=True)
            except Exception as e:
                return sc[0], (0, 0)
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = [ex.submit(work, sc) for sc in scenes]
            for fu in as_completed(futs):
                sid, (ok, bad) = fu.result()
                done += 1; okn += ok; badn += bad
                if done % 25 == 0:
                    print(f"  {done}/{len(scenes)} 条 {okn} 废弃 {badn}", flush=True)
        print("完成", done, "场景，写回", okn, "条，校验失败", badn)
