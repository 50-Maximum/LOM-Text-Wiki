# -*- coding: utf-8 -*-
"""严格版正文地名判定：只认旁白里「你/众人在某处」这种在场语句，宁缺勿错。"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")
con = sqlite3.connect(os.path.join(D, "wiki.db"))
con.row_factory = sqlite3.Row
places = sorted(r[0] for r in con.execute("select name from pages where type='地点'"))
PE = json.load(open(os.path.join(D, "place_edits.json"), encoding="utf-8"))
RENAME = PE.get("rename") or {}

ALIAS = {}
for p in places:
    if "-" in p:
        ALIAS.setdefault(p.split("-", 1)[1], p)
for k, v in RENAME.items():
    ALIAS[k] = v
for k in ["无色广场"]:
    ALIAS[k] = "崆峒-无色广场"

scenes = {r[0] for r in con.execute("select script from scenes")}
have = set()
for f in ["place_manual.json", "place_override.json", "scene_place_infer.json",
          "place_logic.json", "place_infer2.json", "place_infer3.json",
          "place_infer4.json", "place_infer5.json"]:
    p = os.path.join(D, f)
    if os.path.exists(p):
        have |= set(json.load(open(p, encoding="utf-8")).keys())

rows = collections.defaultdict(list)
for r in con.execute("select script,seq,text,speaker from lines order by script,seq"):
    if r["script"] in scenes:
        rows[r["script"]].append((r["seq"], r["text"] or "", r["speaker"] or ""))

PRESENCE = re.compile(r"(你|一行人|众人|两人|三人)[^。！？]{0,10}?"
                      r"(在|来到|走进|进入|回到|返回|经过|登上|穿过|待在|留在|守着|坐镇)"
                      r"[^。！？]{0,10}")

out = {}
for sc, ls in rows.items():
    if sc in have:
        continue
    votes = collections.defaultdict(list)
    for seq, tx, sp in ls:
        if sp and sp != "旁白":
            continue
        for al, p in ALIAS.items():
            if al not in tx:
                continue
            for m in PRESENCE.finditer(tx):
                seg = m.group(0)
                if al in seg:
                    votes[p].append((seq, tx.strip()[:60]))
    if not votes:
        continue
    rank = sorted(votes.items(), key=lambda x: -len(x[1]))
    top, ev = rank[0]
    if len(rank) > 1 and len(rank[1][1]) == len(ev):
        continue
    out[sc] = {"place": top, "src": "正文地名（推断）",
               "why": "旁白「%s」" % ev[0][1], "seq": ev[0][0], "hit": len(ev)}

json.dump(out, open(os.path.join(D, "place_infer6.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
print("严格判定", len(out), "条")
print(collections.Counter(v["place"] for v in out.values()).most_common(12))
for k in list(out)[:14]:
    print("   %-22s → %-13s %s" % (k, out[k]["place"], out[k]["why"]))
