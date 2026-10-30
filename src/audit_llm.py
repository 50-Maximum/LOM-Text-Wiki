# -*- coding: utf-8 -*-
"""两轮 LLM 审查：
A. 势力/地点 类型纠错（地点是地点，门派是门派）
B. 人物门派归属（只认明确证据，出现在某地不算）
用法: python audit_llm.py <api_key> [a|b]
"""
import sqlite3, os, sys, json, time, io, re, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
URL = "https://api.deepseek.com/chat/completions"
KEYFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "key.txt")
KEY = open(KEYFILE, encoding="utf-8").read().strip() if os.path.exists(KEYFILE) else ""
AUTH = "Bea" + "rer " + KEY
PHASE = sys.argv[2] if len(sys.argv) > 2 else "a"

SYS_A = """你是《活侠传》wiki 的审校。判断每个实体属于「势力」还是「地点」。
只输出 JSON：{"items":[{"name":"...","type":"势力|地点","why":"一句依据"}]}
判定标准：
- 地点：可到达、可居住的场所。山、岭、城、镇、村、街、店、客栈、寺、观、庵、楼、阁、院、堂、房、场、洞、谷、林、渡口、战场、秘境。
- 势力：有成员、有组织、能收徒或号令的团体。门派、帮会、教派、世家、联盟、杀手组织。
- 二者同名（如唐门既是门派也是驻地）时按笔记主体判断，倾向「势力」。
- 名字像地点但笔记讲的是组织，就判势力；反之亦然。"""

SYS_B = """你是《活侠传》wiki 的审校。判断每个人物属于哪个门派/势力。
只输出 JSON：{"items":[{"name":"人物名","faction":"势力名或空字符串","evidence":"原文短句"}]}
铁律：
1. 只有明确写出身份才算：弟子、门人、掌门、长老、帮主、教主、世家子弟、拜入、投靠、出身、师承。
2. 仅仅在某地出现、在该地说话、与该派人物有往来，都不算归属。
3. faction 必须从给定候选列表里选，不能自创；没有明确归属就填空字符串。
4. evidence 摘原文里能证明归属的短句，不超过 30 字。"""


def call(sys_prompt, user):
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": sys_prompt},
                     {"role": "user", "content": user}],
        "temperature": 0.1, "max_tokens": 2500,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": AUTH, "Content-Type": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read().decode("utf-8"))
            return json.loads(d["choices"][0]["message"]["content"]).get("items", [])
        except Exception as e:
            if i == 2:
                return []
            time.sleep(2 * (i + 1))
    return []


def batch(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

def notes_for(typ, name, limit=6):
    conn2 = sqlite3.connect(DB)
    try:
        rows = conn2.execute(
            "select chapter,note from ledger where type=? and name=? order by rowid limit ?",
            (typ, name, limit)).fetchall()
    finally:
        conn2.close()
    seen, out = set(), []
    for ch, note in rows:
        if note in seen:
            continue
        seen.add(note)
        out.append(f"[{ch}] {note}")
    return "\n".join(out)


if PHASE == "a":
    rows = c.execute("select type,name from entities where type in ('势力','地点') order by type,name").fetchall()
    todo = [(t, n) for t, n in rows]
    print("审类型", len(todo))
    fixes = []
    def work(chunk):
        block = "\n\n".join(f"类型：{t}\n名称：{n}\n笔记：\n{notes_for(t, n, 5)}" for t, n in chunk)
        return chunk, call(SYS_A, block)
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(work, ch) for ch in batch(todo, 8)]
        done = 0
        for fu in as_completed(futs):
            chunk, items = fu.result()
            done += len(chunk)
            for it in items:
                nm, ty = it.get("name", ""), it.get("type", "")
                if ty in ("势力", "地点"):
                    for t0, n0 in chunk:
                        if n0 == nm and t0 != ty:
                            fixes.append((t0, nm, ty, it.get("why", "")))
            print("  ", done, "/", len(todo), flush=True)
    print("类型纠正", len(fixes))
    for f in fixes:
        print("   ", f)
    json.dump(fixes, open(r"D:\LegendOfMortal Wiki\data\type_fixes.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

else:
    facs = [r[0] for r in c.execute("select name from factions order by name")]
    people = c.execute("select name from entities where type='人物' order by mentions desc").fetchall()
    print("审归属", len(people), "人；候选势力", len(facs))
    cand = "、".join(facs)
    results = {}
    def work(chunk):
        block = "\n\n".join(f"人物：{n}\n笔记：\n{notes_for('人物', n, 6)}" for (n,) in chunk)
        prompt = f"候选势力：{cand}\n\n{block}"
        return [n for (n,) in chunk], call(SYS_B, prompt)
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(work, ch) for ch in batch(people, 8)]
        done = 0
        for fu in as_completed(futs):
            names, items = fu.result()
            done += len(names)
            for it in items:
                results[it.get("name", "")] = (it.get("faction", "") or "", it.get("evidence", ""))
            print("  ", done, "/", len(people), flush=True)
    json.dump(results, open(r"D:\LegendOfMortal Wiki\data\person_faction.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    hit = sum(1 for v in results.values() if v[0])
    print("有明确归属", hit, "/", len(results))
