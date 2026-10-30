# -*- coding: utf-8 -*-
"""把地图事件（PositionEventData）对到剧本：多级规则，记录命中方式。

规则顺序：
  S1 名称+配置值直接拼（alchemy_work_501）
  S2 族前缀 + 结果码百位（door_02 + 501 → door_02_5xx 里唯一/取第一）
  S3 族前缀 + 结果码后两位
  S4 族前缀下唯一剧本
输出 data/position_script_map.json（name → script）与 data/position_map_report.json
"""
import io, sys, re, json, sqlite3, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
ev = json.load(open(WIKI + r"\data\position_events.json", encoding="utf-8"))
c = sqlite3.connect(WIKI + r"\data\wiki.db").cursor()
SCRIPTS = [r[0] for r in c.execute("select script from scenes")]
S = set(SCRIPTS)
byprefix = collections.defaultdict(list)
for s in SCRIPTS:
    m = re.match(r"^(.*?)_\d+$", s)
    byprefix[m.group(1) if m else s].append(s)


def family_forms(nm):
    """返回两种族名写法：全小写、保留原样"""
    s = re.sub(r"(_[A-Za-z]{1,3})?_\d{1,3}$", "", nm)
    s = re.sub(r"_result$", "", s, flags=re.I)
    return list(dict.fromkeys([s.lower(), s]))


def family(nm):
    return family_forms(nm)[0]


def suffix3(sc):
    m = re.search(r"_(\d{3})$", sc)
    return m.group(1) if m else ""


def candidates(d):
    nm, val = d["name"], str(d["value"] or "")
    forms = family_forms(nm)
    extra = []
    for b in forms:
        extra.append(b.replace("ch_", "ch"))
        extra.append(b.replace("Ch_", "ch"))
        if b[:1] in ("S", "s"):
            extra.append("S" + b[1:].lower())
    forms = list(dict.fromkeys(forms + extra))
    outs = []
    m = re.match(r"(?i)section_(\d+)_(\d+)", nm)
    if m:
        sb = "section_%s_free_%s" % (m.group(1), m.group(2))
        outs.append((sb, "SD"))
        if val:
            outs.append((sb + "_" + val, "SD"))
            outs.append((sb + val, "SD"))
    for b in forms + [nm.lower(), nm]:
        if val:
            for v in {val, val.zfill(3)}:
                outs.append((b + "_" + v, "S1"))
                outs.append((b + v, "S1"))
        outs.append((b, "S1"))
    for b in forms:
        pool = byprefix.get(b, [])
        if not pool:
            continue
        if val:
            hun = val[:1]
            same = [s for s in pool if suffix3(s).startswith(hun)]
            if same:
                outs.append((same[0], "S2"))
            tail = val[1:]
            same2 = [s for s in pool if suffix3(s).endswith(tail)]
            if same2:
                outs.append((same2[0], "S3"))
        if len(pool) == 1:
            outs.append((pool[0], "S4"))
    return outs


res, methods = {}, collections.Counter()
for d in ev:
    hit = next(((s, m) for s, m in candidates(d) if s in S), None)
    if hit:
        res[d["name"]] = hit[0]
        methods[hit[1]] += 1
    else:
        methods["未命中"] += 1

json.dump(res, open(WIKI + r"\data\position_script_map.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("命中 %d / %d" % (len(res), len(ev)))
print("方式分布:", dict(methods))
miss = [d for d in ev if d["name"] not in res]
print("\n未命中 %d，样例：" % len(miss))
for d in miss[:10]:
    print("   %-26s key=%-8s val=%s" % (d["name"], d["key"], d["value"]))
