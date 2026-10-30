# -*- coding: utf-8 -*-
"""逐场景解析 Lua 分支树：每个抉择点有哪些选项，每个选项之后发生什么。

产出 data/build/branch_tree.jsonl + 库表 branch_nodes。
用法:
  python build_branch_tree.py --sample S0017_01   # 只跑一场，打印
  python build_branch_tree.py                     # 全量
"""
import os, sys, io, re, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw")
BUILD = os.path.join(BASE, "data", "build")
DB = os.path.join(BASE, "data", "wiki.db")

body = json.load(open(os.path.join(BUILD, "text.json"), encoding="utf-8"))
names = {}
try:
    c0 = sqlite3.connect(DB)
    for sid_, nm in c0.execute("select id, name from names"):
        names[sid_] = nm
    c0.close()
except Exception:
    pass

RX_SAY_KEY = re.compile(r'say\(\s*luamanager\.GetStoryText\(\s*"([^"]+)"\s*\)\s*\)')
RX_SAY_TEXT = re.compile(r'say\(\s*"((?:[^"\\]|\\.)*)"\s*\)')
RX_CHAR = re.compile(r'setcharacter\(\s*(?:characters\.Get\(\s*"([^"]+)"|([A-Za-z_]\w*))')
RX_FLAG = re.compile(r'SetFlag\(\s*"([^"]+)"\s*,\s*([-\d.]+)\s*\)')
RX_STAT = re.compile(r'statmodifymanager\.Player\(\s*"([^"]+)"\s*,\s*([-\d.]+)')
RX_SCENE = re.compile(r'luamanager\.ChangeScene\(\s*"([^"]+)"')
RX_SWITCH = re.compile(r'local\s+(\w+)\s*=\s*checkpointmanager\.Switch\(\s*"([^"]+)"')
RX_COND = re.compile(r'local\s+(\w+)\s*=\s*checkpointmanager\.Condition\(\s*"([^"]+)"')
RX_DICE = re.compile(r'local\s+(\w+)\s*=\s*checkpointmanager\.Dice\(\s*"([^"]+)"')
RX_CHOOSE = re.compile(r'local\s+(\w+)\s*=\s*(?:choosetimer|choose)\(\s*(\w+)')
RX_TAB = re.compile(r'(\w+)\[(\d+)\]\s*=\s*"([^"]*)\|([<>]=?\d+)"')
RX_MENU_TAB = re.compile(r'(\w+)\[(\d+)\]\s*=\s*"([^"|]*)"')
RX_TAB2 = re.compile(r'(\w+)\[(\d+)\]\s*=\s*"([^"|]*)\|([^"]*)"')
RX_TALK = re.compile(r'(\w+)\[(\d+)\]\s*=\s*(?:[\w.]+\s+and\s+)?"([^"]*)"')
IF_RX = re.compile(r'^(if|elseif|else)\b(.*)$')
CMP_RX = re.compile(r'(\w+)\s*==\s*(\d+)')

STAT_NAMES = {"disposition": "性情", "mental": "心相", "behaviour": "处世", "team": "向心"}


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


def unesc(s):
    return s.replace('\\"', '"').replace("\\n", "\n")


def clean_opt(t):
    t0 = (t or "").strip()
    if t0.lower().startswith("exit+"):
        return "结束对话"
    """选项文案清理：去 ~ 前缀、去 |条件 尾巴。"""
    t = (t or "").strip().lstrip("~").strip()
    if "|" in t:
        t = t.split("|", 1)[0].strip()
    return t


def zh(code):
    if not code:
        return ""
    return body.get(code.lstrip("~"), code.lstrip("~"))


def parse_scene(path, sid):
    s = open(path, encoding="utf-8").read()

    dice_tabs = collections.defaultdict(dict)
    tab_pos = collections.defaultdict(list)   # 表名 -> [字符位置]
    tx = RX_TAB.search(s)
    for m in RX_TAB.finditer(s):
        dice_tabs[m.group(1)][int(m.group(2))] = (m.group(3), m.group(4))
        tab_pos[m.group(1)].append(m.start())
    for m in RX_TAB2.finditer(s):
        _nm, _ix, _tx, _cd = m.group(1), int(m.group(2)), m.group(3).strip(), m.group(4)
        if not _tx:
            continue
        if "dice" in _nm.lower():
            dice_tabs[_nm].setdefault(_ix, (_tx, _cd))
            tab_pos[_nm].append(m.start())
    menu_tabs = collections.defaultdict(dict)
    for m in RX_MENU_TAB.finditer(s):
        menu_tabs[m.group(1)].setdefault(int(m.group(2)), m.group(3))
    for m in RX_TAB2.finditer(s):
        _nm, _ix, _tx = m.group(1), int(m.group(2)), m.group(3).strip()
        if _tx and "dice" not in _nm.lower():
            menu_tabs[_nm].setdefault(_ix, _tx)
    for m in RX_TALK.finditer(s):
        _nm, _ix, _val = m.group(1), int(m.group(2)), m.group(3).strip()
        if not _val:
            continue
        if "+" in _val:
            _parts = _val.split("+")
            _kind = _parts[0].strip()
            _lab = (_parts[1].strip() if len(_parts) > 1 else "").strip()
            if _kind == "exit":
                menu_tabs[_nm][_ix] = "结束对话"
                continue
            if _lab:
                menu_tabs[_nm].setdefault(_ix, _lab)
        elif _val != "~x":
            menu_tabs[_nm].setdefault(_ix, _val)
    sw_vars = {m.group(1): m.group(2) for m in RX_SWITCH.finditer(s)}
    cd_vars = {m.group(1): m.group(2) for m in RX_COND.finditer(s)}

    stack = []           # [(indent, node)]
    seq = 0
    speaker = "旁白"
    points = []
    point_by_tbl = {}

    for raw in s.splitlines():
        st = raw.strip()
        if not st or st.startswith("--"):
            continue
        ind = indent_of(raw)
        while stack and stack[-1][0] >= ind:
            stack.pop()

        m = IF_RX.match(st)
        if m:
            kw, rest = m.group(1), m.group(2).strip()
            node = None
            if kw == "else":
                node = {"label": "其余情况", "kind": "else", "tbl": "", "idx": 0,
                        "lines": [], "flags": [], "stats": [], "scenes": []}
            else:
                cm = CMP_RX.search(rest)
                var = cm.group(1) if cm else ""
                val = int(cm.group(2)) if cm else 0
                if var.startswith("choice_"):
                    tbl = var[7:]
                    if tbl in dice_tabs:
                        txt, cond = dice_tabs[tbl].get(val, ("", ""))
                        node = {"label": clean_opt(zh(txt)) or ("结果%d" % val), "kind": "dice",
                                "tbl": tbl, "idx": val, "cond": cond, "code": txt,
                                "lines": [], "flags": [], "stats": [], "scenes": []}
                    else:
                        lab = menu_tabs.get(tbl, {}).get(val, "")
                        if lab.startswith("O_"):
                            lab = zh(lab)
                        node = {"label": clean_opt(lab) or ("（无文案槽位 %d）" % val), "kind": "choose",
                                "tbl": tbl, "idx": val, "cond": "",
                                "lines": [], "flags": [], "stats": [], "scenes": []}
                elif var in sw_vars:
                    node = {"label": "%s=%d" % (var, val), "kind": "switch",
                            "tbl": "", "idx": val, "checkpoint": sw_vars[var],
                            "lines": [], "flags": [], "stats": [], "scenes": []}
                elif var in cd_vars:
                    node = {"label": "%s=%d" % (var, val), "kind": "condition",
                            "tbl": "", "idx": val, "checkpoint": cd_vars[var],
                            "lines": [], "flags": [], "stats": [], "scenes": []}
                else:
                    node = {"label": rest[:40], "kind": "if", "tbl": "", "idx": 0,
                            "lines": [], "flags": [], "stats": [], "scenes": []}
            if node:
                node["ctx"] = [n["label"] for _, n in stack]
                stack.append((ind, node))
                p = point_by_tbl.get(node.get("tbl") or "")
                if p is not None and node["kind"] in ("dice", "choose"):
                    p["arms"].setdefault(node["idx"], node)
            continue

        m = RX_CHOOSE.match(st)
        if m:
            tbl = m.group(2)
            p = {"script": sid, "seq": seq, "kind": "choose", "tbl": tbl,
                 "checkpoint": "", "ctx": [n["label"] for _, n in stack],
                 "options": [], "arms": {}}
            for i in sorted(menu_tabs.get(tbl, {})):
                lab = menu_tabs[tbl][i]
                if lab.startswith("O_"):
                    lab = zh(lab)
                p["options"].append({"idx": i, "text": clean_opt(lab), "cond": ""})
            points.append(p)
            point_by_tbl[tbl] = p
            continue
        m = RX_DICE.match(st)
        if m:
            var, cp = m.group(1), m.group(2)
            # 骰子表不一定与判定同名，取位置上最近的一张骰子表（同 p1 的做法）
            here = s.find(st)
            best, bestd = "", None
            for tname, poss in tab_pos.items():
                if len(dice_tabs[tname]) < 2 or "dice" not in tname:
                    continue
                d = min(abs(p - here) for p in poss)
                if bestd is None or d < bestd:
                    best, bestd = tname, d
            tbl = best or (var[:-7] if var.endswith("_result") else var)
            p = {"script": sid, "seq": seq, "kind": "dice", "tbl": tbl,
                 "checkpoint": cp, "ctx": [n["label"] for _, n in stack],
                 "options": [], "arms": {}}
            for i in sorted(dice_tabs.get(tbl, {})):
                txt, cond = dice_tabs[tbl][i]
                p["options"].append({"idx": i, "text": clean_opt(zh(txt)), "cond": cond,
                                     "code": txt})
            points.append(p)
            point_by_tbl[tbl] = p
            continue

        m = RX_SAY_KEY.search(raw)
        if m:
            seq += 1
            t = (body.get(m.group(1)) or "").replace("\n", " ")[:110]
            for _, n in stack:
                n["lines"].append({"seq": seq, "sp": speaker, "t": t})
            continue
        m = RX_SAY_TEXT.search(raw)
        if m:
            seq += 1
            t = unesc(m.group(1)).replace("\n", " ")[:110]
            for _, n in stack:
                n["lines"].append({"seq": seq, "sp": speaker, "t": t})
            continue
        m = RX_CHAR.match(st)
        if m:
            sid_ = m.group(1) or m.group(2)
            speaker = "旁白" if sid_ in ("narrative", "None") else (names.get(sid_) or sid_)
            continue
        m = RX_FLAG.search(st)
        if m:
            for _, n in stack:
                n["flags"].append({"f": m.group(1), "v": float(m.group(2))})
            continue
        m = RX_STAT.search(st)
        if m:
            for _, n in stack:
                n["stats"].append({"s": STAT_NAMES.get(m.group(1), m.group(1)),
                                   "v": float(m.group(2))})
            continue
        m = RX_SCENE.search(st)
        if m:
            for _, n in stack:
                n["scenes"].append(m.group(1))
            continue

    return points


def summarize(points, sid):
    rows = []
    for p in points:
        for o in p["options"]:
            arm = p["arms"].get(o["idx"])
            rows.append({
                "script": sid, "seq": p["seq"], "kind": p["kind"],
                "checkpoint": p["checkpoint"], "idx": o["idx"],
                "text": o.get("text", ""), "cond": o.get("cond", ""),
                "ctx": " > ".join(p["ctx"]),
                "n_lines": len(arm["lines"]) if arm else 0,
                "flags": json.dumps(arm["flags"] if arm else [], ensure_ascii=False),
                "stats": json.dumps(arm["stats"] if arm else [], ensure_ascii=False),
                "scenes": json.dumps(arm["scenes"] if arm else [], ensure_ascii=False),
                "sample": json.dumps((arm["lines"][:3] if arm else []), ensure_ascii=False),
            })
        # 没有对应选项的臂（比如 elseif 链多出来的）
        for idx, arm in p["arms"].items():
            if any(o["idx"] == idx for o in p["options"]):
                continue
            rows.append({"script": sid, "seq": p["seq"], "kind": p["kind"],
                         "checkpoint": p["checkpoint"], "idx": idx,
                         "text": arm.get("label", ""), "cond": arm.get("cond", ""),
                         "ctx": " > ".join(p["ctx"]), "n_lines": len(arm["lines"]),
                         "flags": json.dumps(arm["flags"], ensure_ascii=False),
                         "stats": json.dumps(arm["stats"], ensure_ascii=False),
                         "scenes": json.dumps(arm["scenes"], ensure_ascii=False),
                         "sample": json.dumps(arm["lines"][:3], ensure_ascii=False)})
    return rows


def main():
    only = None
    if "--sample" in sys.argv:
        only = sys.argv[sys.argv.index("--sample") + 1]
    scdir = os.path.join(RAW, "scripts")
    files = sorted(f for f in os.listdir(scdir) if f.endswith(".txt"))
    if only:
        files = [f for f in files if f[:-4] == only]

    allrows, allpts = [], []
    for fn in files:
        sid = fn[:-4]
        pts = parse_scene(os.path.join(scdir, fn), sid)
        allpts.append({"script": sid, "points": pts})
        allrows.extend(summarize(pts, sid))

    if only:
        print(json.dumps(allpts[0], ensure_ascii=False, indent=1)[:6000])
        return

    with open(os.path.join(BUILD, "branch_tree.jsonl"), "w", encoding="utf-8") as f:
        for r in allpts:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    c = sqlite3.connect(DB)
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript("""drop table if exists branch_nodes;
        create table branch_nodes(script TEXT, seq INT, kind TEXT, checkpoint TEXT,
            idx INT, text TEXT, cond TEXT, ctx TEXT, n_lines INT, flags TEXT,
            stats TEXT, scenes TEXT, sample TEXT);""")
    c.executemany("""insert into branch_nodes values(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  [(r["script"], r["seq"], r["kind"], r["checkpoint"], r["idx"],
                    r["text"], r["cond"], r["ctx"], r["n_lines"], r["flags"],
                    r["stats"], r["scenes"], r["sample"]) for r in allrows])
    c.commit()
    n_pts = sum(len(p["points"]) for p in allpts)
    print("场景", len(allpts), "抉择点", n_pts, "选项行", len(allrows))
    print("有台词的臂", sum(1 for r in allrows if r["n_lines"]),
          "有旗标的臂", sum(1 for r in allrows if r["flags"] != "[]"),
          "有跳转的臂", sum(1 for r in allrows if r["scenes"] != "[]"))


if __name__ == "__main__":
    main()
