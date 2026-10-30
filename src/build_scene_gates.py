# -*- coding: utf-8 -*-
"""场景开场判定：剧本第一句台词之前做的 Switch/Condition 检查，翻成可读要求。

用于事件页在没有「进入条件边」时兜底说明「这一场在什么状态下成立」。
过滤：Talk_Option_XX（对话选项记账）、纯空文本。
输出 data/scene_gates.json：{script: [要求文本, ...]}
"""
import io, sys, os, re, glob, gzip, json, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
LIB = os.path.join(WIKI, "data", "mod_res", "LOMAssistant.conditions.json.gz")
OUT = os.path.join(WIKI, "data", "scene_gates.json")
lib = json.loads(gzip.open(LIB, "rb").read().decode("utf-8"))
SW, CD = lib["Switches"], lib["Conditions"]
SKIP = re.compile(r"^(Talk_Option|TalkOption|XXX)", re.I)


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
        ls = open(f, encoding="utf-8", errors="replace").read().splitlines()
        first_say = next((i for i, l in enumerate(ls) if l.strip().startswith("say(")), len(ls))
        texts = []
        for ln in ls[:first_say]:
            for m in re.finditer(r'checkpointmanager\.(?:Switch|Condition)\("([^"]+)"\)', ln):
                cid = m.group(1)
                if SKIP.match(cid):
                    continue
                t = pretty(cid)
                if t and t not in texts:
                    texts.append(t)
        if texts:
            out[sc] = texts[:4]
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print("场景:", len(out), " 行:", sum(len(v) for v in out.values()))
    for k in list(out)[:6]:
        print("  ", k, out[k])


if __name__ == "__main__":
    main()
