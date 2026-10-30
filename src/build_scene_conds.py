# -*- coding: utf-8 -*-
"""每场剧本用到的判定编号 → 可读要求（来自咖啡伴侣判定库）。

不做行级对齐（对不上，硬对会错），只按场景汇总，保留编号便于核对。
输出 data/scene_conds.json：{脚本: [{"id":..., "text":...}, ...]}
"""
import io, sys, os, re, glob, gzip, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
LIB = os.path.join(WIKI, "data", "mod_res", "LOMAssistant.conditions.json.gz")
OUT = os.path.join(WIKI, "data", "scene_conds.json")
lib = json.loads(gzip.open(LIB, "rb").read().decode("utf-8"))
SW, CD = lib["Switches"], lib["Conditions"]
SKIP = re.compile(r"^(Talk_Option|TalkOption|XXX)$", re.I)


def pretty(cid):
    v = SW.get(cid) or CD.get(cid)
    if isinstance(v, list):
        v = "、".join(str(x) for x in v)
    if not v:
        return ""
    s = str(v)
    for a, b in ((" 需>=", "≥"), (" 需<=", "≤"), (" 需>", "＞"), (" 需<", "＜"), (" 需=", "＝"), (" 需", "")):
        s = s.replace(a, b)
    return s.replace(">=", "≥").replace("<=", "≤")


def main():
    out = {}
    for f in sorted(glob.glob(os.path.join(WIKI, "data", "raw", "scripts", "*.txt"))):
        sc = os.path.splitext(os.path.basename(f))[0]
        t = open(f, encoding="utf-8", errors="replace").read()
        items, seen_t = [], set()
        for m in re.finditer(r'checkpointmanager\.(?:Switch|Condition)\("([^"]+)"\)', t):
            cid = m.group(1)
            if SKIP.match(cid):
                continue
            tx = pretty(cid)
            if not tx or tx in seen_t:
                continue
            if "TalkOption" in tx or "Talk_Option" in tx:
                continue
            seen_t.add(tx)
            items.append({"id": cid, "text": tx})
        if items:
            out[sc] = items[:20]
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print("场景:", len(out), " 判定条目:", sum(len(v) for v in out.values()))
    for k in list(out)[:5]:
        print("  ", k, [x["text"] for x in out[k][:4]])


if __name__ == "__main__":
    main()
