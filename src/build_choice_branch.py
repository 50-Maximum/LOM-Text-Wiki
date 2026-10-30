# -*- coding: utf-8 -*-
"""解析剧本里的选项 → 结果，输出 data/choice_branch.json

结构：
{ "剧本": [ {"var":"option_001", "seq": 18, "options":[
     {"idx":1, "key":"O_..", "text":"一点也不", "cond":"",
      "effects":["处世-1","唐默铃+1"], "lines":["你对我太宽容啦。"],
      "next":"ch5_5_1", "dice":[">=80","<=20"] } ] } ] }

结果内容取自该选项 if 分支块内的：属性变动、好感变动、旗标、台词、跳转剧本、掷骰门槛。
"""
import io, sys, os, re, json, sqlite3, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
SRC = os.path.join(B, "raw", "scripts")
OUT = os.path.join(B, "choice_branch.json")

TEXT = json.load(open(os.path.join(B, "build", "text.json"), encoding="utf-8"))
c = sqlite3.connect(os.path.join(B, "wiki.db")).cursor()
CH = {}
for sid, sp in c.execute("select distinct speaker_id,speaker from lines where speaker_id<>''"):
    CH.setdefault(sid, sp)
CH.update({"player": "赵活"})

STAT = {"disposition": "性情", "mental": "心相", "behaviour": "处世", "team": "向心",
        "attack": "攻击", "defense": "防御", "hp": "气血", "fame": "名声",
        "contribution": "贡献", "money": "银两", "morality": "道德",
        "talking": "嘴力", "medicine": "医术", "cooking": "厨艺", "study": "学问",
        "presence": "修养", "luck": "命运", "agility": "轻功", "internal": "内功"}

RX_BLOCK = re.compile(r"^\s*local\s+(option\w*)\s*=\s*\{\}")
RX_ASSIGN = re.compile(r'^\s*(option\w*)\[(\d+)\]\s*=\s*"([^"]*)"')
RX_CHOOSE = re.compile(r"^\s*local\s+(choice\w*)\s*=\s*choose\((\w+)\)")
RX_IF = re.compile(r"^(if|elseif)\s+(\w+)\s*==\s*(\d+)\s*then\s*$")
RX_PLAYER = re.compile(r'statmodifymanager\.Player\("([^"]+)"\s*,\s*(-?[\d.]+)')
RX_CHAR = re.compile(r'statmodifymanager\.Character\("([^"]+)"\s*,\s*(-?[\d.]+)')
RX_FLAG = re.compile(r'SetFlag\("([^"]+)"\s*,\s*(-?[\d.]+)')
RX_NEXT = re.compile(r'Set(?:Next|CurrentStory|CurrentTravel|Temp)Script\("([^"]+)"|ChangeScene\("([^"]+)"')
RX_STORY = re.compile(r'GetStoryText\("([^"]+)"\)')
RX_SAY = re.compile(r'^\s*say\("(.*)"\)\s*$')
RX_THRESH = re.compile(r'\b(>=|<=|>|<)\s*(\d+)')


def txt_of(key):
    v = TEXT.get(key)
    return (v or "").strip()


def prompt_of(lines, pos):
    """选项前面的那句提示语（玩家看到的提问）。"""
    for i in range(pos - 1, max(-1, pos - 40), -1):
        s = lines[i]
        m = RX_STORY.search(s)
        if m:
            t = txt_of(m.group(1))
            if t:
                return t
        m2 = RX_SAY.match(s)
        if m2:
            t = m2.group(1).replace('\\n', ' ').strip()
            if t:
                return t
    return ""


def parse_script(path):
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    blocks = []            # 每个选项组
    cur = None
    for i, ln in enumerate(lines):
        m = RX_BLOCK.match(ln)
        if m:
            indent = len(ln) - len(ln.lstrip("\t"))
            cur = {"var": m.group(1), "pos": i, "indent": indent, "opts": [], "choicevar": None}
            blocks.append(cur)
            continue
        if cur is not None:
            a = RX_ASSIGN.match(ln)
            if a:
                cur["opts"].append((int(a.group(2)), a.group(3)))
                continue
            ch = RX_CHOOSE.match(ln)
            if ch:
                cur["choicevar"] = ch.group(1)
                cur = None

    out = []
    for b in blocks:
        cv = b["choicevar"]
        if not cv:
            continue
        # 找到各分支（允许选项块本身缩进，如嵌在别的 if 里）
        branches = {}
        start = b["pos"]
        act = None
        base = b["indent"]
        rx_if = re.compile(r"^(\s*)(if|elseif)\s+%s\s*==\s*(\d+)\s*then\s*$" % re.escape(cv))
        for i in range(start, len(lines)):
            s = lines[i]
            m = rx_if.match(s)
            if m and len(m.group(1)) <= base:
                act = int(m.group(3))
                branches.setdefault(act, [])
                continue
            if act is not None:
                ind = len(s) - len(s.lstrip("\t"))
                if s.strip() == "end" and ind <= base:
                    act = None
                    continue
                if s.strip() == "else:" and ind <= base:
                    act = None
                    continue
                branches[act].append(s)
        opts = []
        for idx, val in b["opts"]:
            key = val if re.match(r"^O_", val) else ""
            text = txt_of(val) if key else val
            body = branches.get(idx) or []
            eff, said, nxt, dice = [], [], "", []
            flags = collections.OrderedDict()
            for s in body:
                for k, v in RX_PLAYER.findall(s):
                    nm = STAT.get(k, k)
                    eff.append("%s%+g" % (nm, float(v)))
                for cid, v in RX_CHAR.findall(s):
                    nm = CH.get(cid, cid)
                    eff.append("%s%+g" % (nm, float(v)))
                for f, v in RX_FLAG.findall(s):
                    flags.setdefault(f, [])
                    if v not in flags[f]:
                        flags[f].append(v)
                m2 = RX_NEXT.search(s)
                if m2 and not nxt:
                    nxt = m2.group(1) or m2.group(2) or ""
                for st in RX_STORY.findall(s):
                    t = txt_of(st)
                    if t and t not in said:
                        said.append(t)
                m3 = RX_SAY.match(s)
                if m3:
                    t = m3.group(1).replace('\\n', ' ').strip()
                    if t and t not in said:
                        said.append(t)
                for a, num in RX_THRESH.findall(s):
                    sig = "%s%s" % (a, num)
                    if sig not in dice:
                        dice.append(sig)
            for f, vs in flags.items():
                eff.append("旗标%s＝%s%s" % (f, vs[0], "…" if len(vs) > 1 else ""))
            opts.append({"idx": idx, "key": key, "text": text, "cond": "",
                         "effects": eff, "lines": said[:3], "next": nxt, "dice": dice[:4]})
        if opts:
            out.append({"var": b["var"], "choicevar": cv, "pos": b["pos"],
                        "prompt": prompt_of(lines, b["pos"]), "options": opts})
    return out


def main():
    res, n = {}, 0
    for f in sorted(os.listdir(SRC)):
        if not f.endswith(".txt"):
            continue
        sc = f[:-4]
        r = parse_script(os.path.join(SRC, f))
        if r:
            res[sc] = r
            n += sum(len(x["options"]) for x in r)
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("剧本 %d 个带选项，选项总数 %d" % (len(res), n))
    print("\n=== ch5_4_8_9 样例")
    for blk in (res.get("ch5_4_8_9") or [])[:2]:
        print("  提问：%s" % (blk.get("prompt") or "-")[:30])
        for o in blk["options"]:
            print("  %d. %-8s 结果：%s ｜ 台词：%s ｜ 跳转：%s"
                  % (o["idx"], o["text"][:8], "、".join(o["effects"]) or "-",
                     (o["lines"][0][:24] if o["lines"] else "-"), o["next"] or "-"))


if __name__ == "__main__":
    main()
