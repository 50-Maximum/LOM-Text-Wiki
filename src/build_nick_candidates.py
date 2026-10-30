# -*- coding: utf-8 -*-
"""从正文抽绰号：江湖人称「X」/ 号「X」/ 外号「X」/ 绰号「X」/「X」某某，并尝试绑定人名。

输出 data/nick_candidates.json
"""
import io, json, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(BASE + r"\wiki.db")
c.row_factory = sqlite3.Row

NAMES = sorted({r[0].split("·")[-1] for r in c.execute("select name from pages where type='人物'")},
               key=len, reverse=True)

PAT = [
    re.compile(r"(?:江湖人称|人称|号称|绰号|外号|封号|号)[是为：:]?\s*[「『“\"]([^」』”\"]{2,8})[」』”\"]"),
    re.compile(r"[「『“\"]([^」』”\"]{2,8})[」』”\"]\s*(?:的)?([\u4e00-\u9fff]{2,4})"),
]
out = collections.defaultdict(set)
for r in c.execute("select script,seq,speaker,text from lines"):
    t = r["text"] or ""
    if len(t) < 6:
        continue
    named = [n for n in NAMES if n in t]
    if not named:
        continue
    for p in PAT:
        for m in p.finditer(t):
            nick = m.group(1)
            if not nick or nick == named[0] or len(nick) < 2:
                continue
            if p is PAT[1]:
                who = m.group(2)
                if who not in NAMES:
                    continue
                out[who].add(nick)
            else:
                # 句子里的第一个人名作为归属
                out[named[0]].add(nick)

print("有人名归属的绰号 %d 个" % len(out))
for k in list(out)[:15]:
    print("   %-8s %s" % (k, "、".join(sorted(out[k])[:5])))
json.dump({k: sorted(v) for k, v in out.items()},
          open(BASE + r"\nick_candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
