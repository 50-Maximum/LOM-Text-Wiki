# -*- coding: utf-8 -*-
"""P1 结构解析：章节脚本 -> 场景 / 台词 / 分支 / 选项 / 旗标 / 数值效果。

分支按 tab 缩进还原；每个分支上挂它造成的数值与旗标改动，
这样「结果2」不再是空号，而是「贡献度 +10、精神 -10」这种可读的说明。
"""
import os, re, json, collections

RAW = r"D:\LegendOfMortal Wiki\data\raw"
BUILD = r"D:\LegendOfMortal Wiki\data\build"
os.makedirs(BUILD, exist_ok=True)

CJK = re.compile(r"[\u4e00-\u9fff]")
TAG = re.compile(r"\{/?(?:size|color|punch|title|b|i)(?:=[^}]*)?\}")

RX_SAY_KEY = re.compile('say\\(\\s*luamanager\\.GetStoryText\\(\\s*"([^"]+)"\\s*\\)\\s*\\)')
RX_SAY_TEXT = re.compile('say\\(\\s*"((?:[^"\\\\]|\\\\.)*)"\\s*\\)')
RX_CHAR = re.compile('setcharacter\\(\\s*(?:characters\\.Get\\(\\s*"([^"]+)"|([A-Za-z_]\\w*))')
RX_DIALOG = re.compile('setsaydialog\\(\\s*saydialogs\\.(\\w+)')
RX_FLAG = re.compile('SetFlag\\(\\s*"([^"]+)"\\s*,\\s*([-\\d.]+)\\s*\\)')
RX_DICE = re.compile('checkpointmanager\\.Dice\\(\\s*"([^"]+)"')
RX_RESULT = re.compile('local\\s+(\\w+)_result\\s*=\\s*checkpointmanager\\.Dice\\(\\s*"([^"]+)"')
RX_TAB = re.compile('(\\w+)\\[(\\d+)\\]\\s*=\\s*"([^"]*)\\|([<>]=?\\d+)"')
RX_CHOICEVAR = re.compile('local\\s+(choice_\\w+)\\s*=\\s*(?:choosetimer|choose)\\(\\s*(\\w+)')
RX_CHOOSE = re.compile('local\\s+(choice_\\w+)\\s*=\\s*choose\\(\\s*(\\w+)')
RX_MENU_TAB = re.compile('(\\w+)\\[(\\d+)\\]\\s*=\\s*"([^"|]*)"')
RX_TAB2 = re.compile('(\\w+)\\[(\\d+)\\]\\s*=\\s*"([^"|]*)\\|([^"]*)"')
RX_SWITCH = re.compile('local\\s+(\\w+)_result\\s*=\\s*checkpointmanager\\.Switch\\(\\s*"([^"]+)"')
RX_COND = re.compile('local\\s+(\\w+)_result\\s*=\\s*checkpointmanager\\.Condition\\(\\s*"([^"]+)"')
RX_STAT = re.compile('statmodifymanager\\.Player\\(\\s*"([^"]+)"\\s*,\\s*([-\\d.]+)')
RX_OPT = re.compile('"(O_[^"|]+)\\|([^"]*)"')
RX_OPT2 = re.compile('"(O_[^"|]+)"')

SCAN = re.compile(
    'setcharacter\\([^\\n]*|setsaydialog\\([^\\n]*|'
    'say\\(\\s*luamanager\\.GetStoryText\\([^\\n]*|'
    'say\\(\\s*"[^\\n]*|'
    'SetFlag\\([^\\n]*|checkpointmanager\\.Dice\\([^\\n]*|'
    'statmodifymanager\\.Player\\([^\\n]*|'
    'local\\s+choice_\\w+\\s*=\\s*choose\\([^\\n]*|'
    'luamanager\\.ChangeScene\\([^\\n]*|'
    '"O_[^"]*\\|[^"]*"')

IF_RX = re.compile('^(if|elseif|else)\\b(.*)$')
CMP_RX = re.compile('(\\w+)\\s*==\\s*(\\d+)')

ESC = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}

ALIAS = {"stone1": "飞石帮众", "stone2": "飞石帮众", "stones": "飞石帮众",
         "picture1": "旁白·画卷", "picture2": "旁白·画卷", "picture3": "旁白·画卷",
         "picture4": "旁白·画卷", "picture5": "旁白·画卷"}

PLACE_PARENT = {
    "大门": "唐门", "正心堂": "唐门", "练功场": "唐门", "炼丹房": "唐门",
    "伙房": "唐门", "锻冶场": "唐门", "讲经堂": "唐门", "后山": "唐门",
    "男弟子房": "唐门", "女弟子房": "唐门", "外堡": "唐门", "茶肆": "唐门",
    "药铺": "唐门", "义田": "唐门", "温泉": "唐门", "闹市": "唐门",
    "飞天殿": "崆峒", "夺魄森林": "崆峒", "铁拳巷": "崆峒", "玄功洞": "崆峒",
    "夺魄峰": "崆峒", "无色广场": "崆峒",
    "常风观": "青城", "上清宫": "青城", "青城山镇": "青城",
}

PLACE_PREFIX = {
    "alchemy": "炼丹房", "forge": "锻冶场", "kitchen": "伙房", "door": "大门",
    "backmountain": "后山", "study": "讲经堂", "center": "练功场",
    "room1": "男弟子房", "room2": "女弟子房", "mall": "正心堂",
    "downtown": "闹市", "secret": "神秘房子",
    "section_01_01": "飞天殿", "section_01_02": "夺魄森林",
    "section_01_03": "铁拳巷", "section_01_04": "玄功洞",
    "section_01_05": "夺魄峰", "section_01_06": "无色广场",
    "section_02_01": "常风观", "section_02_02": "上清宫",
    "section_02_03": "青城山镇",
}
TRAITS = ("道德", "处世", "性情", "修养", "学问", "嘴力", "名声", "胆识")

PLACE_WORDS = ["飞天殿", "夺魄森林", "铁拳巷", "玄功洞", "夺魄峰", "无色广场",
               "常风观", "上清宫", "青城山镇", "唐门", "后山", "伙房", "炼丹房",
               "正心堂", "讲经堂", "锻冶场", "大门", "男弟子房", "女弟子房",
               "闹市", "外堡", "茶肆", "药铺", "义田", "温泉", "练功场",
               "夺魄", "青城", "崆峒", "锦香宫", "南宫世家", "飞石帮"]

TIER_NAMES = {
    "性情": ["慞弱", "谨慎", "中庸", "勇敢", "莽夫"],
    "处世": ["矫情", "知礼", "中庸", "豪爽", "粗鲁"],
    "道德": ["恶棍", "坏人", "中庸", "好人", "侠客"],
    "修养": ["疯狂", "暴躁", "中庸", "沉着", "君子"],
}
TIER_BOUNDS = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100)]
TIER_RX = re.compile('(道德|处世|性情|修养|嘴力|心相)\\s*需\\s*(<=|>=|<|>)\\s*(\\d+)')
TIME_RX = re.compile('目前时间\\s*需\\s*(>=|<=|=|>|<)\\s*第([一二三四五六七八九十]+)年([一二三四五六七八九十]+)月(上旬|中旬|下旬)')
XUN = {"上旬": 1, "中旬": 2, "下旬": 3}
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
      "七": 7, "八": 8, "九": 9, "十": 10}


def cn2int(s):
    if not s:
        return 0
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN.get(s[1:], 0)
    if s.endswith("十"):
        return CN.get(s[:-1], 0) * 10
    if "十" in s:
        a, b = s.split("十")
        return CN.get(a, 0) * 10 + CN.get(b, 0)
    return CN.get(s, 0)


def time_key(y, m, x):
    return y * 10000 + m * 100 + XUN.get(x, 0)


def tier_tokens(attr, op, val):
    names = TIER_NAMES.get(attr)
    if not names:
        return []
    try:
        v = float(val)
    except Exception:
        return []
    out = []
    for i, (lo, hi) in enumerate(TIER_BOUNDS):
        if op in ("<=", "<") and lo < v:
            out.append(attr + ":" + names[i])
        elif op in (">=", ">") and hi > v:
            out.append(attr + ":" + names[i])
    return out


def unescape(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            out.append(ESC.get(s[i + 1], s[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def plain(t):
    return TAG.sub("", unescape(t))


def indent_of(line):
    n = 0
    for ch in line:
        if ch == "\t":
            n += 4
        elif ch == " ":
            n += 1
        else:
            break
    return n


def load_kv(path):
    d = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip().lstrip("\ufeff")
        if not line or " = " not in line:
            continue
        k, v = line.split(" = ", 1)
        d[k.strip()] = v
    return d


def strip_ns(key):
    return key.split("/", 1)[1] if "/" in key else key


def main():
    raw_text = json.load(open(os.path.join(BUILD, "text.json"), encoding="utf-8"))
    text = {k: unescape(v) for k, v in raw_text.items()}
    body = {k: plain(v) for k, v in raw_text.items()}

    system = {}
    for fn in os.listdir(os.path.join(RAW, "system")):
        system[fn.replace(".txt", "")] = load_kv(os.path.join(RAW, "system", fn))
    names = {strip_ns(k): v for k, v in system.get("Character_zh-cn", {}).items()}
    stats = {strip_ns(k): v for k, v in system.get("Stat_zh-cn", {}).items()
             if k.startswith("PlayerStat/")}
    switches = {}
    conds = {}
    cpath = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"
    if os.path.exists(cpath):
        _cj = json.load(open(cpath, encoding="utf-8"))
        switches = _cj.get("Switches", {})
        conds = _cj.get("Conditions", {})

    places = {}
    for k, v in system.get("Position_zh-cn", {}).items():
        if k.startswith("Position/Name/"):
            places[k.split("/")[-1].lower()] = v
    works = {}
    for k, v in system.get("Work_zh-cn", {}).items():
        if k.startswith("Work/Content/"):
            works[k.split("/")[-1].lower()] = v

    lines, scenes, flags, choices, branch_rows = [], [], [], [], []
    scdir = os.path.join(RAW, "scripts")
    files = sorted(f for f in os.listdir(scdir) if f.endswith(".txt"))
    src_count = collections.Counter()

    for fn in files:
        sid = fn[:-4]
        s = open(os.path.join(scdir, fn), encoding="utf-8").read()

        tables = collections.defaultdict(dict)
        tbl_at = []
        for m in RX_TAB.finditer(s):
            tables[m.group(1)][m.group(2)] = {"raw": m.group(3),
                                              "label": m.group(3).lstrip("~"),
                                              "cond": m.group(4)}
            tbl_at.append((m.start(), m.group(1)))
        for m in RX_TAB2.finditer(s):
            _nm, _ix, _txt, _cd = m.group(1), m.group(2), m.group(3), m.group(4)
            if _txt.strip() and not (tables.get(_nm, {}).get(_ix) or {}).get("label"):
                tables[_nm][_ix] = {"raw": _txt.strip(),
                                    "label": _txt.strip().lstrip("~"), "cond": _cd}
        choice_var = {m.group(1): m.group(2) for m in RX_CHOICEVAR.finditer(s)}
        menu_tabs = collections.defaultdict(dict)
        for m in RX_MENU_TAB.finditer(s):
            menu_tabs[m.group(1)][m.group(2)] = m.group(3)
        menu_blocks = {}
        switch_map = {m.group(1): m.group(2) for m in RX_SWITCH.finditer(s)}
        cond_map = {m.group(1): m.group(2) for m in RX_COND.finditer(s)}
        effects = collections.defaultdict(list)

        speaker, mode, seq = None, "character", 0
        first_key = last_key = None
        dice_at = []
        stack = []
        battle_total = 0
        tier_set = set()
        texts = []

        base = 0
        for raw in s.splitlines():
            stripped = raw.strip()
            ind = indent_of(raw)
            active = stripped and not stripped.startswith("--")
            if active:
                while stack and stack[-1][0] >= ind:
                    stack.pop()
            m_if = IF_RX.match(stripped) if active else None
            if m_if:
                kind, rest = m_if.group(1), m_if.group(2)
                if kind == "else":
                    label = "其余情况"
                else:
                    cm = CMP_RX.search(rest)
                    if cm:
                        var, val = cm.group(1), cm.group(2)
                        if var.startswith("choice_"):
                            tb = choice_var.get(var, var[7:])
                            opt = tables.get(tb, {}).get(val)
                            if opt:
                                raw = opt.get("raw", "")
                                txt = body.get(raw, "") if raw.startswith("O_") else opt.get("label", "")
                                label = ("%s｜掷骰%s" % (txt[:18], opt["cond"])) if txt \
                                    else ("骰子结果%s（%s）" % (val, opt["cond"]))
                            else:
                                blk = menu_blocks.get(var)
                                lab = ""
                                try:
                                    lab = blk["options"][int(val) - 1]["label"] if blk else ""
                                except Exception:
                                    lab = ""
                                label = lab or ("选项%s" % val)
                        elif var.startswith("cond_"):
                            ck = cond_map.get(var[:-5], "")
                            txt = conds.get(ck, "")
                            for mm2 in TIER_RX.finditer(str(txt)):
                                tier_set.update(tier_tokens(mm2.group(1), mm2.group(2), mm2.group(3)))
                            label = ("条件 %s｜%s" % (ck, txt[:26])) if ck else ("条件分支%s" % val)
                        elif var.startswith("switch_"):
                            ck = switch_map.get(var[:-7], "")
                            reqs = switches.get(ck, [])
                            short = reqs[0] if reqs else ""
                            for rq in reqs:
                                for mm2 in TIER_RX.finditer(str(rq)):
                                    tier_set.update(tier_tokens(mm2.group(1), mm2.group(2), mm2.group(3)))
                            if ck.startswith(("Battle_Result", "Combat_Result")):
                                label = "战胜" if val == "1" else ("战败" if val == "0" else ("战斗结果%s" % val))
                            else:
                                label = ("条件 %s｜%s" % (ck, short[:26])) if ck else ("条件分支%s" % val)
                        elif "attle" in var:
                            label = "战斗结果%s" % val
                        else:
                            label = "%s=%s" % (var, val)
                    else:
                        label = "条件 %s" % rest.replace(" then", "").strip()[:30]
                stack.append((ind, label))
            branch = " > ".join(l for _, l in stack)

            for m in SCAN.finditer(raw):
                t, pos = m.group(0), base + m.start()
                if t.startswith("setcharacter"):
                    cm = RX_CHAR.match(t)
                    if cm:
                        speaker = cm.group(1) or cm.group(2)
                elif t.startswith("setsaydialog"):
                    dm = RX_DIALOG.match(t)
                    if dm:
                        mode = dm.group(1)
                elif "GetStoryText" in t:
                    sm = RX_SAY_KEY.search(t)
                    if not sm:
                        continue
                    key = sm.group(1)
                    seq += 1
                    first_key = first_key or key
                    last_key = key
                    src_count["table"] += 1
                    lines.append({"script": sid, "seq": seq, "key": key,
                                  "text": text.get(key, ""), "plain": body.get(key, ""),
                                  "speaker_id": None if speaker in (None, "narrative") else speaker,
                                  "speaker": "旁白" if speaker in (None, "narrative") else (names.get(speaker) or ALIAS.get(speaker) or speaker),
                                  "mode": mode, "branch": branch})
                    texts.append(body.get(key, ""))
                elif t.startswith("say("):
                    sm = RX_SAY_TEXT.search(t)
                    if not sm:
                        continue
                    key = "%s#%d" % (sid, seq + 1)
                    seq += 1
                    first_key = first_key or key
                    last_key = key
                    src_count["inline"] += 1
                    lines.append({"script": sid, "seq": seq, "key": key,
                                  "text": unescape(sm.group(1)), "plain": plain(sm.group(1)),
                                  "speaker_id": None if speaker in (None, "narrative") else speaker,
                                  "speaker": "旁白" if speaker in (None, "narrative") else (names.get(speaker) or ALIAS.get(speaker) or speaker),
                                  "mode": mode, "branch": branch})
                    texts.append(plain(sm.group(1)))
                elif t.startswith("local choice_") and "choose(" in t:
                    mm = RX_CHOOSE.match(t)
                    if mm:
                        var, tb = mm.group(1), mm.group(2)
                        opts = []
                        for idx in sorted(menu_tabs.get(tb, {}), key=lambda x: int(x)):
                            raw = menu_tabs[tb][idx]
                            seg = [x for x in raw.split("+") if x and x != "x"]
                            if len(seg) >= 2 and seg[0].lower() == "talk":
                                lab = "闲聊｜" + names.get(seg[-1], seg[-1])
                            elif len(seg) >= 2:
                                pl = places.get(seg[0].lower(), "")
                                act = works.get(seg[-1].lower(), "")
                                lab = "%s｜%s" % (pl or seg[0], act or seg[-1]) if (pl or act) else raw
                            else:
                                lab = raw
                            opts.append({"key": "", "label": lab, "text": lab, "cond": ""})
                        if opts:
                            blk = {"script": sid, "seq": seq, "checkpoint": "",
                                   "options": opts, "branch": branch}
                            choices.append(blk)
                            menu_blocks[var] = blk
                elif t.startswith("luamanager.ChangeScene"):
                    if "Battle" in t:
                        battle_total += 1
                        if branch:
                            mm = re.search('"([^"]+)"', t)
                            if mm:
                                effects[branch].append({"kind": "battle", "id": mm.group(1),
                                                        "name": "对决 " + mm.group(1), "value": ""})
                elif t.startswith("statmodifymanager.Player"):
                    sm = RX_STAT.search(t)
                    if sm and branch:
                        effects[branch].append({"kind": "stat", "id": sm.group(1),
                                                "name": stats.get(sm.group(1), sm.group(1)),
                                                "value": sm.group(2)})
                elif t.startswith("SetFlag"):
                    fm = RX_FLAG.match(t)
                    if fm:
                        flags.append({"script": sid, "seq": seq, "flag": fm.group(1),
                                      "value": fm.group(2), "after_key": last_key,
                                      "branch": branch})
                        if branch:
                            effects[branch].append({"kind": "flag", "id": fm.group(1),
                                                    "name": fm.group(1), "value": fm.group(2)})
                elif t.startswith("checkpointmanager.Dice"):
                    dm = RX_DICE.match(t)
                    if dm:
                        block = {"script": sid, "seq": seq, "checkpoint": dm.group(1),
                                 "options": [], "branch": branch}
                        dice_at.append((pos, block))
                        choices.append(block)
            base += len(raw) + 1

        # 每个判定挂最近的一张骰子表（表可能写在 Dice 之前或之后）
        for dpos, blk in dice_at:
            best = None
            for tp, tb in tbl_at:
                if len(tables[tb]) < 2 or "dice" not in tb:
                    continue
                dist = abs(tp - dpos)
                if best is None or dist < best[0]:
                    best = (dist, tb)
            if not best:
                continue
            tb = best[1]
            opts = []
            for idx in sorted(tables[tb], key=lambda x: int(x)):
                o = tables[tb][idx]
                raw = o["raw"]
                if raw.startswith("O_"):
                    opts.append({"key": raw, "label": "",
                                 "text": body.get(raw, ""), "cond": o["cond"]})
                else:
                    raw = o["raw"]
                    lab = o["label"]
                    if "+" in raw and not raw.startswith("~"):
                        seg = [x for x in raw.split("+") if x and x != "x"]
                        if len(seg) >= 2:
                            pl = places.get(seg[0].lower(), "")
                            act = works.get(seg[-1].lower(), "")
                            if pl or act:
                                lab = "%s｜%s" % (pl or seg[0], act or seg[-1])
                    opts.append({"key": "", "label": lab,
                                 "text": lab, "cond": o["cond"]})
            if opts and not blk["options"]:
                blk["options"] = opts

        for br, eff in effects.items():
            branch_rows.append({"script": sid, "branch": br, "effects": eff})

        place = ""
        low = sid.lower()
        for k, v in PLACE_PREFIX.items():
            if low.startswith(k) and len(k) > len(place):
                place = v
        if not place and texts:
            blob = "\n".join(texts)
            cnt = collections.Counter()
            for pw in PLACE_WORDS:
                n = blob.count(pw)
                if n:
                    cnt[pw] = n
            if cnt:
                best, n = cnt.most_common(1)[0]
                if n >= 2:
                    place = best

        root = PLACE_PARENT.get(place, place)
        if place and root and place != root:
            place = root + "-" + place

        # 时间窗与行动点：从本脚本用到的开关条件中抽取
        tlo = thi = 0
        tlo_s = thi_s = ""
        act_min = 0
        for ck in set(switch_map.values()) | set(cond_map.values()):
            for rq in (switches.get(ck) or ([conds[ck]] if ck in conds else [])):
                s_rq = str(rq)
                mm = TIME_RX.search(s_rq)
                if mm:
                    op = mm.group(1)
                    k = time_key(cn2int(mm.group(2)), cn2int(mm.group(3)), mm.group(4))
                    lab = "第%s年%s月%s" % (mm.group(2), mm.group(3), mm.group(4))
                    if op in (">=", ">", "=") and k > tlo:
                        tlo, tlo_s = k, lab
                    if op in ("<=", "<", "=") and (not thi or k < thi):
                        thi, thi_s = k, lab
                ma = re.search("行动次数\\s*需\\s*>=\\s*(\\d+)", s_rq)
                if ma:
                    act_min = max(act_min, int(ma.group(1)))

        battles = battle_total
        traits = sorted({t for br in effects for t in TRAITS if t in br})

        scenes.append({"script": sid, "lines": seq, "cjk": len(CJK.findall(s)),
                       "first_key": first_key, "last_key": last_key,
                       "place": place, "root": root, "battles": battles,
                       "traits": "、".join(traits), "tiers": " ".join(sorted(tier_set)),
                       "time_from": tlo_s, "time_to": thi_s,
                       "tkey": tlo or thi, "actions": act_min})

    def dump(name, rows):
        with open(os.path.join(BUILD, name), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    dump("lines.jsonl", lines)
    dump("scenes.jsonl", scenes)
    dump("flags.jsonl", flags)
    dump("choices.jsonl", choices)
    dump("branches.jsonl", branch_rows)

    stats_out = {
        "lines": len(lines),
        "by_source": dict(src_count),
        "scenes": len(scenes),
        "empty_scenes": sum(1 for x in scenes if x["lines"] == 0),
        "empty_text": sum(1 for l in lines if not l["plain"]),
        "lines_with_branch": sum(1 for l in lines if l["branch"]),
        "flags": len(flags),
        "choices": len(choices),
        "choices_with_options": sum(1 for c in choices if c["options"]),
        "branches_with_effects": len(branch_rows),
    }
    with open(os.path.join(BUILD, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats_out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: stats_out[k] for k in ("lines", "lines_with_branch",
                                                "choices", "choices_with_options",
                                                "branches_with_effects")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
