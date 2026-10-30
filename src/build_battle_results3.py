# -*- coding: utf-8 -*-
"""战斗胜负判定 v3：按「变量最近一次赋值」归属分支，修掉同脚本复用同名变量导致的串台。"""
import io, json, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
SW = re.compile(r'local\s+(\w+)\s*=\s*checkpointmanager\.Switch\("((?:Combat|Battle)_Result_[^"]+)"\)')
BR = re.compile(r'^\s*(?:if|elseif)\s+(\w+)\s*==\s*(\d+)\s+then\s*$')

def indent_of(line):
    return len(line) - len(line.lstrip("\t "))

def judge(t, sc):
    if re.search(r'ChangeScene\("(?:Combat|Battle)",\s*"%s"' % re.escape(sc), t):
        return "败"
    if 'ChangeScene("GameOver' in t:
        return "败"
    if ("SetNextScript" in t) or ("SetCurrentStoryScript" in t) or ('ChangeScene("Free"' in t):
        return "胜"
    if re.search(r'statmodifymanager\.Player\("life",\s*-\d', t):
        return "败"
    return ""

out, stat = {}, collections.Counter()
for fn in os.listdir(RAW):
    if not fn.endswith(".txt"):
        continue
    sc = fn[:-4]
    lines = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read().splitlines()
    assign = []          # (lineno, var, switch)
    for i, ln in enumerate(lines):
        m = SW.search(ln)
        if m:
            assign.append((i, m.group(1), m.group(2)))
    if not assign:
        continue
    for i, ln in enumerate(lines):
        m = BR.match(ln)
        if not m:
            continue
        var, res = m.group(1), int(m.group(2))
        prev = [a for a in assign if a[0] < i and a[1] == var]
        if not prev:
            continue
        sw = prev[-1][2]
        ind = indent_of(ln)
        j, body = i + 1, []
        while j < len(lines):
            s = lines[j]
            if indent_of(s) == ind and s.strip() in ("end", "else"):
                break
            if indent_of(s) == ind and s.strip().startswith(("elseif", "if ")):
                break
            body.append(s)
            j += 1
        lb = judge("\n".join(body), sc)
        if lb:
            out.setdefault(sc, {}).setdefault(sw, {})[str(res)] = lb

# 只保留胜负两向齐全的
clean = {}
for sc, d in out.items():
    dd = {sw: mp for sw, mp in d.items() if "胜" in mp.values() and "败" in mp.values()}
    if dd:
        clean[sc] = dd

dirs = collections.defaultdict(set)
for sc, d in clean.items():
    for sw, mp in d.items():
        for res, lb in mp.items():
            dirs[(sw, res)].add(lb)
conflict = [(k, sorted(v)) for k, v in dirs.items() if len(v) > 1]

json.dump(clean, open(os.path.join(BASE, "data", "battle_results_block.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("判定出胜负 %d 个剧本" % len(clean))
print("开关方向分布:")
for k in sorted(dirs):
    print("   ", k, sorted(dirs[k]))
print("冲突:", conflict)

