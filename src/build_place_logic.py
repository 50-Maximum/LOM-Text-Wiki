# -*- coding: utf-8 -*-
"""用前后剧情的走位线索推导地点。

思路：一场戏的地点，先看自身正文有没有明确的空间线索（舟上／夜市／客栈／城门…），
再看它在剧情段里的顺序——若前一场在某地、本场开头没有「出发/下山/启程」这类动身语，
就承前场的地点；若本场出现动身语又没有明说目的地，就只能算「途中」。

输出 data/place_logic.json：{script: {place, src, quote, conf}}
不覆盖「脚本编号 / 场景标题」这类硬证据，只补空缺与修正仅靠词频得出的地点。
"""
import io, sys, os, json, sqlite3, re, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()

PREFIX = ("alchemy", "forge", "kitchen", "door", "backmountain", "study", "center",
          "room1", "room2", "mall", "downtown", "secret",
          "section_01_01", "section_01_02", "section_01_03", "section_01_04",
          "section_01_05", "section_01_06", "section_02_01", "section_02_02", "section_02_03")

# 正文里的空间线索 → 具体地名（眉山是唐门所在的县镇）
CUES = [
    (r"(客舟|舟中|船舱|出舱|船上|船头|船尾|渡船|小舟|江上|水路)", "岷江"),
    (r"(夜市|市集|街上|街头|摊子|摊位|铺子|集市|镇上|村镇)", "眉山"),
    (r"(客栈|客房|上房|店小二|酒家|酒楼)", "眉山"),
    (r"(医馆|药铺|药堂|诊金)", "千金方医馆"),
    (r"(城门|城墙|进城|出城)", "眉山"),
    (r"(林间|林中|森林|林子)", "森林"),
    (r"(上山|山道|山路|登山)", "唐门-登山道"),
]
TRAVEL = re.compile(r"(下山|上山|启程|动身|出发|告辞|离去|告别|返回|回到|赶往|前往|抵达|来到|远行|赶路|回山)")

SG = json.load(open(os.path.join(B, "data", "story_segments.json"), encoding="utf-8"))
seg_scenes = {s["id"]: (s.get("scenes") or []) for s in SG.get("segments") or []}
seg_of = SG.get("seg_of") or {}

sc_info = {r[0]: {"place": r[1] or "", "title": r[2] or ""}
           for r in c.execute("select script,coalesce(place,''),coalesce(title,'') from scenes")}


def text_of(script, limit=120):
    rows = c.execute("""select text from lines where script=? order by seq limit ?""",
                     (script, limit)).fetchall()
    return "\n".join((r[0] or "") for r in rows)


def narr_of(script, limit=40):
    rows = c.execute("""select text from lines where script=? and speaker='旁白'
                        order by seq limit ?""", (script, limit)).fetchall()
    return "\n".join((r[0] or "") for r in rows)


def strong(script):
    p = sc_info.get(script, {}).get("place") or ""
    if not p:
        return "", ""
    low = script.lower()
    if any(low.startswith(k) for k in PREFIX):
        return p, "脚本编号"
    return "", ""      # 其余当前都算弱证据，允许被走位线索修正


def cue_of(txt):
    for rx, place in CUES:
        m = re.search(rx, txt)
        if m:
            return place, m.group(0)
    return "", ""


out = {}
stat = collections.Counter()

for sid, scenes_ in seg_scenes.items():
    prev_place = ""
    for i, sc in enumerate(scenes_):
        if sc not in sc_info:
            continue
        sp, sp_src = strong(sc)
        if sp:
            prev_place = sp
            stat["硬证据"] += 1
            continue
        txt = text_of(sc)
        head = "\n".join(txt.split("\n")[:3])
        cp, cueword = cue_of(head)          # 只看开头三句，避免对话里顺口提及被当成地点
        moved = bool(TRAVEL.search(head))
        has_place = bool(sc_info.get(sc, {}).get("place"))
        if cp and (not has_place or moved):
            # 开头就交代了场所，且与现有弱证据不同 → 采用开头这一句
            out[sc] = {"place": cp, "src": "正文线索", "quote": cueword, "conf": "中"}
            prev_place = cp
            stat["正文线索"] += 1
        elif not has_place:
            np_, nw = cue_of(narr_of(sc))
            _boat = re.search(r"(客舟|舟中|船舱|出舱|船上|船头|船尾|小舟)", txt)
            if not np_ and _boat:
                out[sc] = {"place": "岷江", "src": "正文线索", "quote": _boat.group(0), "conf": "中"}
                prev_place = "岷江"
                stat["正文线索"] += 1
            elif np_:
                out[sc] = {"place": np_, "src": "旁白线索", "quote": nw, "conf": "中"}
                prev_place = np_
                stat["旁白线索"] += 1
            elif moved and not cp:
                out[sc] = {"place": "途中", "src": "动身无目的地",
                           "quote": TRAVEL.search(head).group(0), "conf": "低"}
                prev_place = "途中"
                stat["途中"] += 1
            elif prev_place:
                out[sc] = {"place": prev_place, "src": "承前场", "quote": "", "conf": "中"}
                stat["承前场"] += 1

json.dump(out, open(os.path.join(B, "data", "place_logic.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("推出 %d 场：%s" % (len(out), dict(stat)))
print("\n=== 抽样（正文线索）")
for sc, v in list(out.items())[:12]:
    print("  %-22s %-10s %-8s %s" % (sc, v["place"], v["src"], v["quote"]))
print("\n=== S0003 段结果")
for sc in seg_scenes.get(seg_of.get("S0003_02_02") or "", []):
    print("  %-24s %s" % (sc, out.get(sc, sc_info.get(sc, {}).get("place") or "空")))
