# -*- coding: utf-8 -*-
"""批量生成全部人物/势力/地点的百科简介（编号脚注+逐字引文），写入 intros_char.json / intros_world.json。
已有手写简介的条目跳过。用法: python build_intros_all.py run [model] | sample <类型> <名字>
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

SYS = """你是《活侠传》wiki 编辑。为一则条目写百科简介。只输出 JSON：
{"text":"...","footnotes":[{"n":1,"text":"...","script":"...","quote":"..."}]}
铁律：
1. text 是 120~280 字的简介，尽量全面：出身/身份/师承、关键作为、与主线的关系。涉及结局必须写清「如果…那么…」的分支；禁止「音信渐断」「下落不明」这类含糊表述——百科要讲清楚每条路线的收尾。
2. 文中在关键断言处插入（1）（2）编号，最多 5 个，与 footnotes 一一对应。
3. 每条 footnote：text 一句 15~40 字说明该证据；script 与 quote 必须取自所给笔记——quote 逐字复制笔记的引文（含标点），不得改写、拼接、编造；script 复制对应笔记的 script。
4. 只写所给笔记里实际发生的事，不写推测、评价、游戏机制。笔记不足就写短些，宁缺勿滥。
5. 不写「没有一条线是全都发生」这类解释游戏机制的话。"""

def norm(s):
    return re.sub(r"\s+", "", s or "")

def call(model, prompt):
    body = json.dumps({"model": model,
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": prompt}],
                       "temperature": 0.1, "max_tokens": 2200,
                       "response_format": {"type": "json_object"}}).encode("utf-8")
    for i in range(3):
        try:
            req = urllib.request.Request(URL, data=body,
                                         headers={"Authorization": AUTH, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.loads(r.read().decode("utf-8"))
            return json.loads(d["choices"][0]["message"]["content"])
        except Exception:
            if i == 2:
                return None
            time.sleep(2 * (i + 1))
    return None

def one(model, typ, name, rows):
    rows = rows[:45]
    block = f"条目：{typ}「{name}」\n以下是从各场景抽取的笔记（含逐字引文）：\n"
    for sc, a, note, q in rows:
        block += f"- {sc}#{a} {note} | {q}\n"
    r = call(model, block)
    if not r:
        return name, None, "无响应"
    text = r.get("text") or ""
    fns = r.get("footnotes") or []
    c2 = sqlite3.connect(DB)
    try:
        ok = []
        for fn in fns:
            sc = fn.get("script") or ""
            q = fn.get("quote") or ""
            if "#" in sc:
                sc = sc.split("#")[0]
            if not sc or not q:
                continue
            hit = c2.execute("""select count(*) from lines where script=?
                                and replace(replace(replace(text,char(10),''),char(13),''),' ','') like ?""",
                             (sc, f"%{norm(q)}%")).fetchone()[0]
            if hit:
                ok.append({"n": fn.get("n") or len(ok) + 1, "text": fn.get("text") or "",
                           "script": sc, "quote": q})
    finally:
        c2.close()
    if not ok:
        return name, None, "脚注全不通过"
    seq = sorted(ok, key=lambda x: int(x["n"] or 0))
    nf = []
    new_text = text
    for i, fn in enumerate(seq, 1):
        old = fn["n"]
        if old != i:
            new_text = new_text.replace(f"（{old}）", f"（{i}）")
        nf.append({"n": i, "text": fn["text"], "script": fn["script"], "quote": fn["quote"]})
    return name, {"text": new_text, "footnotes": nf}, ""

def collect():
    c = sqlite3.connect(DB)
    have = {}
    for _fn in ("intros_char.json", "intros_world.json"):
        _p = os.path.join(BASE, "data", _fn)
        if os.path.exists(_p):
            have.update(json.load(open(_p, encoding="utf-8")))
    FINTRO = json.load(open(os.path.join(BASE, "data", "factions_fix.json"), encoding="utf-8")).get("intro", {})
    for k in FINTRO:
        have.setdefault(k, None)
    kids = {r[0] for r in c.execute("select slug from place_children")}
    todo = []
    for typ, slug_prefix, tname in (("人物", "人物/", "人物"), ("势力", "势力/", "势力"), ("地点", "地点/", "地点")):
        for (n,) in c.execute("select distinct name from notes where type=? order by name", (tname,)):
            slug = slug_prefix + n
            if slug in kids or slug in have:
                continue
            rows = c.execute("""select script,seq_from,note,quote from notes
                                where type=? and name=? order by script,seq_from""", (tname, n)).fetchall()
            if rows:
                todo.append((typ, n, rows))
    c.close()
    return todo

def main():
    todo = collect()
    print("待生成:", len(todo), "（人物/势力/地点）", flush=True)
    if len(sys.argv) >= 2 and sys.argv[1] == "sample":
        typ, name = sys.argv[2], sys.argv[3]
        model = sys.argv[4] if len(sys.argv) > 4 else "deepseek-chat"
        for t, n, rows in todo:
            if t == typ and n == name:
                print(one(model, t, n, rows))
                break
        return
    model = sys.argv[2] if len(sys.argv) > 2 else "deepseek-chat"
    out_char = {}; out_world = {}
    done = 0; fail = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(one, model, t, n, rows): (t, n) for t, n, rows in todo}
        for fu in as_completed(futs):
            t, n = futs[fu]
            try:
                name, res, err = fu.result()
            except Exception as e:
                name, res, err = n, None, str(e)
            if res:
                (out_char if t == "人物" else out_world)[f"{t}/{name}"] = res
                done += 1
            else:
                fail.append((t, name, err))
            print(f"[{done}/{len(todo)}] {t}/{name} {'OK' if res else 'FAIL ' + err[:40]}", flush=True)
    cp = os.path.join(BASE, "data", "intros_char.json")
    wp = os.path.join(BASE, "data", "intros_world.json")
    for fn, d in ((cp, out_char), (wp, out_world)):
        base = json.load(open(fn, encoding="utf-8"))
        for k, v in d.items():
            if k not in base:
                base[k] = v
        json.dump(base, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("写入完成：人物", len(out_char), "势力/地点", len(out_world), "失败", len(fail))

if __name__ == "__main__":
    main()
