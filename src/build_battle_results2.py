# -*- coding: utf-8 -*-
"""战斗胜负判定 v2：只认剧本结构证据，按优先级收紧判定，避免把「下一场战斗」误判成重打。

判定顺序：
1) 分支里 ChangeScene("Combat"/"Battle", "<本剧本>")  → 重打 = 败
2) 分支里 ChangeScene("GameOver"…)                   → 败
3) 分支里有推进剧情（SetNextScript / SetCurrentStoryScript / ChangeScene("Free")) → 胜
4) 分支里扣生命/体力且无推进                          → 败
5) 其余不给标签
"""
import io, json, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
SW = re.compile(r'local\s+(\w+)\s*=\s*checkpointmanager\.Switch\("((?:Combat|Battle)_Result_[^"]+)"\)')
BR = re.compile(r'^\s*(?:if|elseif)\s+(\w+)\s*==\s*(\d+)\s+then\s*$')

def indent_of(line):
    return len(line) - len(line.lstrip("\t "))

def blocks(lines, var):
    out, i, n = [], 0, len(lines)
    while i < n:
        m = BR.match(lines[i])
        if m and m.group(1) == var:
            ind, res = indent_of(lines[i]), int(m.group(2))
            j, body = i + 1, []
            while j < n:
                s = lines[j]
                if indent_of(s) == ind and s.strip() in ("end", "else"):
                    break
                if indent_of(s) == ind and s.strip().startswith(("elseif", "if ")):
                    break
                body.append(s)
                j += 1
            out.append((res, body))
            i = j
            continue
        i += 1
    return out

def judge(body, sc):
    t = "\n".join(body)
    if re.search(r'ChangeScene\("(?:Combat|Battle)",\s*"%s"' % re.escape(sc), t):
        return "败"
    if 'ChangeScene("GameOver' in t:
        return "败"
    if ("SetNextScript" in t) or ("SetCurrentStoryScript" in t) or ('ChangeScene("Free"' in t):
        return "胜"
    if re.search(r'statmodifymanager\.Player\("life",\s*-\d', t):
        return "败"
    return ""

out, stat, conflict = {}, collections.Counter(), []
for fn in os.listdir(RAW):
    if not fn.endswith(".txt"):
        continue
    sc = fn[:-4]
    lines = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read().splitlines()
    txt = "\n".join(lines)
    for m in SW.finditer(txt):
        var, sw = m.group(1), m.group(2)
        bs = blocks(lines, var)
        if not bs:
            continue
        labels = {res: judge(body, sc) for res, body in bs}
        if "胜" in labels.values() and "败" in labels.values():
            out.setdefault(sc, {})[sw] = {str(k): v for k, v in labels.items() if v}
            stat[sw.split("_")[0] + "_" + sw[-2:]] += 1

# 同一开关在不同剧本里方向是否一致
dirs = collections.defaultdict(set)
for sc, d in out.items():
    for sw, mp in d.items():
        for res, lb in mp.items():
            dirs[(sw, res)].add(lb)
for k, v in dirs.items():
    if len(v) > 1:
        conflict.append((k, sorted(v)))

json.dump(out, open(os.path.join(BASE, "data", "battle_results.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("判定出胜负 %d 个剧本" % len(out))
print("方向冲突的开关:", conflict[:6], "共", len(conflict))
print("样例:", list(out.items())[:4])
