# -*- coding: utf-8 -*-
"""抽取事件「触发条件」。严格 1:1 挂接，宁缺勿错。

挂接规则：
  A. scene_time：脚本 → 攻略事件名，直接采用该攻略事件的条件（最强证据）
  B. guide_index：某脚本只对应唯一一条攻略事件时，采用其「触发……」「备注……」原文
     脚本对应多条攻略事件 → 丢弃（避免把章节开场条件算到章节内每个小事件头上）
  C. guide_events.cond：主线事件条件段（配合 scene_time 对照）
所有文本均照录攻略原文，只做分句与分类标注，不改写。
"""
import io, sys, os, re, json, sqlite3, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
DB = os.path.join(WIKI, "data", "wiki.db")
OUT = os.path.join(WIKI, "data", "event_cond.json")
REAL = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(WIKI, "data", "raw", "scripts", "*.txt"))}

STOP = ("频率", "备注", "路线", "事件获得", "事件奖励", "游戏脚本", "选项", "提示", "惩罚", "影响", "关键", "游戏ID")
STAT_WORDS = ("好感", "名声", "医术", "炼丹", "学问", "道德", "处世", "修养", "贡献", "向心", "心相",
              "门派规模", "武学", "体力", "内力", "轻功", "魅力", "命运", "性情", "嘴力", "行为", "团队")
PLACE_CH = re.compile(r"(房|场|堂|山|门|楼|宫|堡|市|街|店|馆|寺|湖|村|镇|城|谷|关|岛|驿|居|阁|轩|院|洞|崖|桥)")


def clean(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", "", s)


def parse_scripts(cell):
    out = []
    for m in re.finditer(r"([A-Za-z][A-Za-z0-9_]{3,})", cell or ""):
        nm = m.group(1)
        if nm.lower().endswith(".txt"):
            nm = nm[:-4]
        if nm in REAL:
            out.append(nm)
    return list(dict.fromkeys(out))


def clause_label(t):
    if "🚩" in t:
        return "旗标"
    if re.search(r"(概率|随机)触发", t):
        return "概率"
    if re.search(r"事件后|触发|完成.*后", t):
        return "前置"
    if "心上人" in t:
        return "数值"
    if any(w in t for w in STAT_WORDS):
        return "数值"
    if re.search(r"(进入|前往|在|地点：)", t) and PLACE_CH.search(t):
        return "地点"
    if "行动" in t and "消耗" in t:
        return "消耗"
    if "择一" in t or "互斥" in t:
        return "互斥"
    return "条件"


def rows_from(seg, src):
    seg = re.sub(r"游戏ID[0-9A-Za-z\-]*", "", seg)
    seg = seg.strip("|·、")
    rows = []
    for cl in [p for p in re.split(r"[，,；;]", seg) if p]:
        cl = cl.strip()
        if len(cl) < 3:
            continue
        rows.append({"kind": clause_label(cl), "text": cl, "src": src})
    return rows


def main():
    c = sqlite3.connect(DB).cursor()
    # 1. 攻略条目
    g_rows, g_names = {}, {}
    for nm, scell, body in c.execute("select name,scripts,body from guide_index"):
        b = clean(body)
        rows = []
        i = b.find("触发")
        if i >= 0:
            seg = b[i + 2:]
            for st in STOP:
                j = seg.find(st)
                if j > 0:
                    seg = seg[:j]
            rows += rows_from(seg, "攻略·触发") if seg else []
        j = b.find("备注")
        if j >= 0:
            note = b[j + 2:]
            for st in ("事件获得", "游戏脚本", "选项", "提示"):
                k = note.find(st)
                if k > 0:
                    note = note[:k]
            if 3 <= len(note) <= 60:
                rows.append({"kind": "备注", "text": note, "src": "攻略·备注"})
        if not rows:
            continue
        for sc in parse_scripts(scell):
            g_rows.setdefault(sc, []).append((nm, rows))
            g_names.setdefault(sc, set()).add(nm)

    # 2. 主线条件
    ge = {}
    for nm, cond, place in c.execute("select name,cond,place from guide_events"):
        rows = []
        if cond:
            seg = clean(cond)
            for st in ("选择：", "☯事件", "🎲天运", "👉选择", "事件内容", "【", "影响", "提示"):
                k = seg.find(st)
                if k > 0:
                    seg = seg[:k]
            seg = seg.strip("|·、")
            if 3 <= len(seg) <= 90:
                rows += rows_from(seg, "攻略·主线条件")
        if place:
            rows.append({"kind": "地点", "text": clean(place), "src": "攻略·地点"})
        if rows:
            ge[nm] = rows

    # 3. scene_time
    st_map = {}
    for sc, ev in c.execute("select script,event from scene_time"):
        if sc in REAL and ev:
            st_map.setdefault(sc, ev)

    per_script = {}
    for sc, ev in st_map.items():
        rows = list(ge.get(ev, []))
        for nm, r in g_rows.get(sc, []):
            if nm == ev:
                rows += [x for x in r if x not in rows]
        if rows:
            per_script[sc] = rows
    ev_per_script = {}
    for nm, sc in c.execute("select name,script from notes where type='事件'"):
        ev_per_script.setdefault(sc, set()).add(nm)
    for sc, lst in g_rows.items():
        if sc in per_script:
            continue
        if len(g_names.get(sc, ())) == 1:
            # 章节脚本内含多个事件时，攻略给的是整章入口条件，不能算到每个小事件头上
            if len(ev_per_script.get(sc, ())) > 2:
                continue
            per_script[sc] = lst[0][1]

    ev_scripts = {}
    for nm, sc in c.execute("select name,script from notes where type='事件'"):
        ev_scripts.setdefault(nm, []).append(sc)

    res, kindc, nrows = {}, {}, 0
    for nm, scs in ev_scripts.items():
        rows = []
        for sc in scs:
            for r in per_script.get(sc, []):
                if r not in rows:
                    rows.append(r)
        if rows:
            res[nm] = rows
            nrows += len(rows)
            for r in rows:
                kindc[r["kind"]] = kindc.get(r["kind"], 0) + 1
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("脚本挂接:", len(per_script), " scene_time:", len(st_map))
    print("事件页 %d，有触发条件 %d (%.1f%%)，共 %d 行" % (len(ev_scripts), len(res), 100.0 * len(res) / len(ev_scripts), nrows))
    print("分类:", sorted(kindc.items(), key=lambda x: -x[1]))
    for nm in list(res)[:10]:
        print("\n【%s】" % nm)
        for r in res[nm][:5]:
            print("   %s｜%s" % (r["kind"], r["text"][:80]))


if __name__ == "__main__":
    main()
