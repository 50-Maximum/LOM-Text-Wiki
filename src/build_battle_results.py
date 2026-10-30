# -*- coding: utf-8 -*-
"""按剧本结构判定战斗结果分支的胜负，而不是猜开关编号。

判定依据（只认结构证据）：
- 分支里 ChangeScene("Combat"/"Battle") 回到同一场 → 重打 = 失败
- 分支里 ChangeScene("GameOver"...) → 失败
- 分支里扣生命/体力 statmodifymanager.Player("life", -N) → 失败
- 另一支直接推进剧情 → 胜利
输出 data/battle_results.json：{script: {switch: {result: "胜"/"败"}}}
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
    """取 var 的所有 if/elseif 分支：(result, [lines])"""
    out = []
    i = 0
    n = len(lines)
    while i < n:
        m = BR.match(lines[i])
        if m and m.group(1) == var:
            ind = indent_of(lines[i])
            res = int(m.group(2))
            j = i + 1
            body = []
            while j < n:
                s = lines[j]
                if indent_of(s) == ind and s.strip() in ("end", "else"):
                    break
                if indent_of(s) == ind and (s.strip().startswith("elseif") or s.strip().startswith("if ")):
                    break
                body.append(s)
                j += 1
            out.append((res, body))
            i = j
            continue
        i += 1
    return out

def judge(body, script):
    t = "\n".join(body)
    if 'ChangeScene("Combat"' in t or 'ChangeScene("Battle"' in t:
        if script in t:
            return "败"
        return "败"
    if 'ChangeScene("GameOver' in t:
        return "败"
    if re.search(r'statmodifymanager\.Player\("life",\s*-\d', t):
        return "败"
    if 'SetNextScript' in t or 'SetCurrentStoryScript' in t or 'ChangeScene("Free"' in t:
        return "胜"
    return ""

out, stat = {}, collections.Counter()
for fn in os.listdir(RAW):
    if not fn.endswith(".txt"):
        continue
    sc = fn[:-4]
    lines = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read().splitlines()
    for m in SW.finditer("\n".join(lines)):
        var, sw = m.group(1), m.group(2)
        bs = blocks(lines, var)
        if not bs:
            continue
        labels = {res: judge(body, sc) for res, body in bs}
        if "胜" in labels.values() and "败" in labels.values():
            out.setdefault(sc, {})[sw] = {str(k): v for k, v in labels.items() if v}
            stat[sw.split("_")[0]] += 1

json.dump(out, open(os.path.join(BASE, "data", "battle_results.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("判定出胜负的剧本 %d 个（%s）" % (len(out), dict(stat)))
for sc in list(out)[:6]:
    print("   ", sc, json.dumps(out[sc], ensure_ascii=False))
