# -*- coding: utf-8 -*-
"""P2 建库：P0b/P1 产物 -> SQLite + 全文索引。

检索：单字空格 + FTS5 短语，支持中文任意子串；索引只含台词正文，
说话人另走 LIKE（否则搜「布衣」会把他说过的每句话都命中）。
"""
import os, re, json, sqlite3, time, collections

RAW = r"D:\LegendOfMortal Wiki\data\raw"
BUILD = r"D:\LegendOfMortal Wiki\data\build"
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
COND = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"

CHAP = re.compile(r"^ch(\d+)_")


def load_jsonl(name):
    p = os.path.join(BUILD, name)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def load_kv(path):
    d = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip().lstrip("\ufeff")
        if not line or " = " not in line:
            continue
        k, v = line.split(" = ", 1)
        d[k.strip()] = v
    return d


def chapter_of(script):
    m = CHAP.match(script)
    if m:
        return "第%s章" % m.group(1)
    if script.lower().startswith("act"):
        return "序章"
    if script.lower().startswith("talk"):
        return "角色线"
    if script.lower().startswith("s") and script[:1].isdigit() is False:
        return "支线"
    return "其他"


def uni(s):
    return " ".join(ch for ch in s if not ch.isspace())


def main():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
    PRAGMA journal_mode=WAL;
    CREATE TABLE lines(id INTEGER PRIMARY KEY, script TEXT, seq INT, key TEXT,
        text TEXT, speaker TEXT, speaker_id TEXT, mode TEXT, branch TEXT, uni TEXT);
    CREATE TABLE scenes(script TEXT PRIMARY KEY, chapter TEXT, line_count INT,
        cjk INT, first_key TEXT, last_key TEXT, place TEXT, root TEXT, battles INT, traits TEXT, tiers TEXT,
        time_from TEXT, time_to TEXT, tkey INT, actions INT);
    CREATE TABLE flags(id INTEGER PRIMARY KEY, script TEXT, seq INT, flag TEXT,
        value TEXT, after_key TEXT, branch TEXT);
    CREATE TABLE choices(id INTEGER PRIMARY KEY, script TEXT, seq INT,
        checkpoint TEXT, options TEXT);
    CREATE TABLE names(id TEXT PRIMARY KEY, name TEXT);
    CREATE TABLE kv(ns TEXT, key TEXT, value TEXT, PRIMARY KEY(ns, key));
    CREATE TABLE cond(id TEXT PRIMARY KEY, attrs TEXT);
    CREATE TABLE chk(id TEXT PRIMARY KEY, title TEXT);
    CREATE TABLE branches(script TEXT, branch TEXT, effects TEXT, PRIMARY KEY(script, branch));
    CREATE TABLE flaginfo(flag TEXT PRIMARY KEY, label TEXT);
    CREATE TABLE entries(ns TEXT, eid TEXT, kind TEXT, title TEXT, body TEXT,
        PRIMARY KEY(ns, eid, kind));
    CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
    """)

    lines = load_jsonl("lines.jsonl")
    cur.executemany(
        "INSERT INTO lines(script,seq,key,text,speaker,speaker_id,mode,branch,uni) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        [(l["script"], l["seq"], l["key"], l["text"], l["speaker"],
          l["speaker_id"], l["mode"], l.get("branch", ""),
          uni(l.get("plain") or l["text"])) for l in lines])

    by_script = collections.Counter(l["script"] for l in lines)
    cur.executemany("INSERT INTO scenes VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    [(s["script"], chapter_of(s["script"]), by_script.get(s["script"], 0),
                      s["cjk"], s["first_key"], s["last_key"],
                      s.get("place", ""), s.get("root", ""), s.get("battles", 0), s.get("traits", ""),
                      s.get("tiers", ""), s.get("time_from", ""), s.get("time_to", ""),
                      s.get("tkey", 0), s.get("actions", 0))
                     for s in load_jsonl("scenes.jsonl")])

    cur.executemany("INSERT INTO flags(script,seq,flag,value,after_key,branch) VALUES(?,?,?,?,?,?)",
                    [(f["script"], f["seq"], f["flag"], f["value"], f["after_key"],
                      f.get("branch", ""))
                     for f in load_jsonl("flags.jsonl")])
    cur.executemany("INSERT INTO choices(script,seq,checkpoint,options) VALUES(?,?,?,?)",
                    [(c["script"], c["seq"], c["checkpoint"],
                      json.dumps(c.get("options", []), ensure_ascii=False))
                     for c in load_jsonl("choices.jsonl")])
    cur.executemany("INSERT OR REPLACE INTO branches(script,branch,effects) VALUES(?,?,?)",
                    [(b["script"], b["branch"],
                      json.dumps(b.get("effects", []), ensure_ascii=False))
                     for b in load_jsonl("branches.jsonl")])

    # 系统表
    for fn in os.listdir(os.path.join(RAW, "system")):
        ns = fn[:-4]
        rows = []
        for k, v in load_kv(os.path.join(RAW, "system", fn)).items():
            key = k.split("/", 1)[1] if "/" in k else k
            rows.append((ns, key, v))
            if ns == "Character_zh-cn":
                cur.execute("INSERT OR REPLACE INTO names VALUES(?,?)", (key, v))
        cur.executemany("INSERT OR REPLACE INTO kv VALUES(?,?,?)", rows)

    # 判定标题
    dh = os.path.join(RAW, "system", "DiceHeader_zh-cn.txt")
    if os.path.exists(dh):
        rows = []
        for k, v in load_kv(dh).items():
            key = k.split("/", 1)[1] if "/" in k else k
            rows.append((key, v))
        cur.executemany("INSERT OR REPLACE INTO chk VALUES(?,?)", rows)

    # 条件字典
    if os.path.exists(COND):
        cd = json.load(open(COND, encoding="utf-8"))
        rows = []
        for cid, reqs in cd.get("Switches", {}).items():
            rows.append((cid, json.dumps(reqs, ensure_ascii=False)))
        for cid, txt in cd.get("Conditions", {}).items():
            rows.append((cid + "@cond", json.dumps(
                [txt] if isinstance(txt, str) else txt, ensure_ascii=False)))
        cur.executemany("INSERT OR REPLACE INTO cond VALUES(?,?)", rows)

    # 旗标释义：Flag_zh-cn 的 Flag/Name/XXX + 条件表里的「名称 (编号)」
    fi = {}
    for k, v in load_kv(os.path.join(RAW, "system", "Flag_zh-cn.txt")).items():
        if k.startswith("Flag/Name/"):
            fi[k.split("/")[-1]] = v
    if os.path.exists(COND):
        cd0 = json.load(open(COND, encoding="utf-8"))
        rx = re.compile(r"(.+?)\s*\((\w+)\)")
        for reqs in cd0.get("Switches", {}).values():
            for r in reqs:
                mm = rx.search(r)
                if mm and mm.group(2) not in fi:
                    fi[mm.group(2)] = mm.group(1).strip()
    cur.executemany("INSERT OR REPLACE INTO flaginfo VALUES(?,?)", list(fi.items()))

    # 词条配对：Title/Name + Desc
    flat = {}
    for row in cur.execute("SELECT ns,key,value FROM kv"):
        flat.setdefault(row[0], {})[row[1]] = row[2]
    ent = []
    for ns, d in flat.items():
        ids = {}
        for k, v in d.items():
            parts = k.split("/")
            if len(parts) == 2:
                if parts[0] in ("Title", "Name", "Desc", "Text", "Intro"):
                    ids.setdefault(parts[1], {})[parts[0]] = v
                elif parts[0].startswith("CharacterIntro"):
                    ids.setdefault(parts[1], {}).setdefault("variants", []).append(
                        (parts[0], v))
        for eid, parts in ids.items():
            title = parts.get("Title") or parts.get("Name") or eid
            body = parts.get("Desc") or parts.get("Text") or parts.get("Intro") or ""
            if parts.get("variants"):
                body = "\n\n".join("[%s] %s" % (n, v) for n, v in sorted(parts["variants"]))
            ent.append((ns, eid, "entry", title, body))
    cur.executemany("INSERT OR REPLACE INTO entries VALUES(?,?,?,?,?)", ent)

    cur.execute("CREATE VIRTUAL TABLE lines_fts USING fts5(uni, content='lines', "
                "content_rowid='id', tokenize='unicode61')")
    cur.execute("INSERT INTO lines_fts(lines_fts) VALUES('rebuild')")
    cur.execute("CREATE INDEX idx_lines_script ON lines(script)")
    cur.execute("CREATE INDEX idx_lines_speaker ON lines(speaker)")

    manifest = json.load(open(r"D:\LegendOfMortal Wiki\data\manifest.json", encoding="utf-8"))
    meta = {
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "game": manifest["game"],
        "sources": json.dumps({k: v["sha256"] for k, v in manifest["sources"].items()}),
        "version": time.strftime("%Y.%m.%d"),
    }
    cur.executemany("INSERT OR REPLACE INTO meta VALUES(?,?)", list(meta.items()))
    con.commit()

    for t in ("lines", "scenes", "flags", "choices", "names", "kv", "cond", "chk", "branches", "flaginfo", "entries"):
        print(t, cur.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0])
    con.close()
    print("db size MB:", round(os.path.getsize(DB) / 1048576, 1))


if __name__ == "__main__":
    main()
