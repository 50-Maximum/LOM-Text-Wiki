# -*- coding: utf-8 -*-
"""用 pro 模型写路线页：入口、互斥、关键节点、角色命运。

读 data/routes_raw.json，写 routes 表。
用法: python build_routes.py [limit]
"""
import os, sys, json, time, io, sqlite3, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
DB = os.path.join(BASE, "data", "wiki.db")
KF = os.path.join(BASE, "data", "key.txt")
fh = open(KF, "r", encoding="utf-8"); KEY = fh.read().strip(); fh.close()
AUTH = "Bea" + "rer " + KEY
URL = "https://api.deepseek.com/chat/completions"

SYS = """你是《活侠传》的剧情编辑。根据给出的场景清单与原文片段，写一条路线条目。
只输出 JSON：
{"name":"路线名","summary":"150~260字概述，说明这条线怎么走、和别线差在哪",
 "entry":"从哪个抉择/条件进入，20~60字",
 "exclusive":["与之互斥的路线名"],
 "beats":[{"chapter":"第5章","title":"场景名","what":"这一场在这条线里的意义，15~40字"}],
 "fates":[{"who":"角色名","fate":"这条线里此人的结局/去向","evidence":"依据的场景名"}],
 "uncertain":["拿不准的地方"]}
铁律：
1. 只能根据给出的场景名和原文片段推断，不得引入未给出的剧情。
2. 场景清单里可能混入共用场景（不属于这条线独有的），不要把共用场景写成该线专属。
3. 互斥只在有明确证据（同一抉择的不同选项、或文本明说）时填写；否则留空数组。
4. 命运只写这条线里被改变的结果；不知道就写进 uncertain。
5. 不要写「玩家」「游戏机制」，用剧情语言。"""


def call(prompt, tries=3):
    body = json.dumps({"model": "deepseek-v4-pro",
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": prompt}],
                       "temperature": 0.2, "max_tokens": 2600,
                       "response_format": {"type": "json_object"}}).encode("utf-8")
    req = urllib.request.Request(URL, data=body,
                                 headers={"Authorization": AUTH, "Content-Type": "application/json"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read().decode("utf-8"))
            return json.loads(d["choices"][0]["message"]["content"])
        except Exception as e:
            if i == tries - 1:
                print("  调用失败", str(e)[:80])
                return None
            time.sleep(3 * (i + 1))
    return None


def main():
    raw = json.load(open(os.path.join(BASE, "data", "routes_raw.json"), encoding="utf-8"))
    c = sqlite3.connect(DB)
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript("""drop table if exists routes;
        create table routes(flag TEXT PRIMARY KEY, name TEXT, summary TEXT, entry TEXT,
                            exclusive TEXT, beats TEXT, fates TEXT, uncertain TEXT);""")
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 99
    done = 0
    for fid, pack in raw.items():
        if done >= limit:
            break
        reqs = pack["requires"][:60]
        lines = [f"路线：{pack['name']}（旗标 {fid}）", "", "关联场景（按章节）："]
        for x in reqs:
            lines.append(f"- {x['chapter']}｜{x['title']}")
        if pack["sets"]:
            lines.append("")
            lines.append("入口场景原文：")
            for s in pack["sets"]:
                lines.append(f"【{s['chapter']}｜{s['title']}｜值{s['values']}】")
                lines.append(s.get("opening", "")[:1000])
        if pack["cooccur"]:
            lines.append("")
            lines.append("同场共现的其他路线旗标：" +
                         "、".join(f"{x['name']}({x['n']})" for x in pack["cooccur"]))
        prompt = "\n".join(lines)
        out = call(prompt)
        if not out:
            continue
        c.execute("insert or replace into routes values(?,?,?,?,?,?,?,?)",
                  (fid, out.get("name") or pack["name"], out.get("summary", ""),
                   out.get("entry", ""), json.dumps(out.get("exclusive", []), ensure_ascii=False),
                   json.dumps(out.get("beats", []), ensure_ascii=False),
                   json.dumps(out.get("fates", []), ensure_ascii=False),
                   json.dumps(out.get("uncertain", []), ensure_ascii=False)))
        c.commit()
        done += 1
        print(f"[{done}] {fid} {out.get('name')}｜互斥 {out.get('exclusive')}", flush=True)
    print("完成", done)


if __name__ == "__main__":
    main()
