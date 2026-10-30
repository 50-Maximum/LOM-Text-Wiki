# -*- coding: utf-8 -*-
"""把「势力」实体再分类：真门派/帮会/教派/世家/联盟/政权/军队/地点/人群，
并给出应合并到的规范名。"""
import sqlite3, os, sys, json, time, io, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
URL = "https://api.deepseek.com/chat/completions"
KEYFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "key.txt")
KEY = open(KEYFILE, encoding="utf-8").read().strip()
AUTH = "Bea" + "rer " + KEY

SYS = """你是《活侠传》wiki 的审校。给每个条目归类。
只输出 JSON：{"items":[{"name":"原名","kind":"门派|帮会|教派|世家|联盟|政权|军队|地点|人群|其他","canonical":"规范名或原名","why":"一句依据"}]}
判定：
- 门派：有掌门、弟子、武学的武术门派（含分舵，分舵保留原名）。
- 帮会：丐帮、飞石帮、白鲨帮这类以帮众结社的团体。
- 教派：宗教或邪教性质，如极乐教、泥教、五毒教、巫灵教。
- 世家：以家族血脉为核心，如南宫世家、上官世家、宇文世家。
- 联盟：多派联合体，如武林盟、西武林盟、六大派。
- 政权：国家或朝廷，如金国、西夏、蒙古、吐蕃、大理段氏、朝廷。
- 军队：宋军、内戒营这类武装建制。
- 地点：只是地名或建筑，不是团体，如青城山、嵩山、六道峡、龙马潭、白风寨、养龙苑、松烟阁。
- 人群：临时并称或几个人的合称，如岱岳双英、花城四少、极乐七仙、嵩山寺十八铜人。
- 同一事物多种写法时，canonical 填最常用的那个（如「上官家」→「上官世家」，「全真」→「全真派」，「岭南剑派」→「岭南派」，「广东唐门」「广州唐门」→「唐门」，「崆峒铁拳门」→「铁拳门」，「泥教地狱道」→「地狱道」）。"""


def notes(name, limit=5):
    conn = sqlite3.connect(DB)
    try:
        rows = conn.execute("select chapter,note from ledger where type='势力' and name=? "
                            "order by rowid limit ?", (name, limit)).fetchall()
    finally:
        conn.close()
    seen, out = set(), []
    for ch, note in rows:
        if note in seen:
            continue
        seen.add(note)
        out.append(f"[{ch}] {note}")
    return "\n".join(out)


def call(user):
    body = json.dumps({"model": "deepseek-chat",
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": user}],
                       "temperature": 0.1, "max_tokens": 2500,
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
names = [r[0] for r in conn.execute("select name from entities where type='势力' order by mentions desc")]
conn.close()

out = {}
for i in range(0, len(names), 10):
    chunk = names[i:i + 10]
    block = "\n\n".join(f"名称：{n}\n笔记：\n{notes(n)}" for n in chunk)
    for it in call(block):
        if it.get("name") in chunk:
            out[it["name"]] = (it.get("kind", "其他"), it.get("canonical") or it["name"], it.get("why", ""))
    print(i + len(chunk), "/", len(names), flush=True)

json.dump(out, open(r"D:\LegendOfMortal Wiki\data\org_kinds.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for n in names:
    k = out.get(n)
    print(f"   {n:<12} {k[0] if k else '?':<4} → {k[1] if k else ''}")
