# -*- coding: utf-8 -*-
"""列出 Combat_Result_01/02 各剧本的结构判定，并抽样看分歧剧本的分支内容。"""
import io, json, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
d = json.load(open(os.path.join(BASE, "data", "battle_results.json"), encoding="utf-8"))
by = collections.defaultdict(list)
for sc, sws in d.items():
    for sw, mp in sws.items():
        by[(sw, mp.get("1"))].append(sc)
for k in sorted(by):
    print("%-18s res1=%-2s 剧本 %d：%s" % (k[0], k[1], len(by[k]), ", ".join(by[k][:8])))

# 看分歧剧本里 res1 分支到底做了什么
def blocks_of(sc, var):
    lines = open(os.path.join(RAW, sc + ".txt"), encoding="utf-8", errors="ignore").read().splitlines()
    out, i = [], 0
    while i < len(lines):
        m = re.match(r'^\s*(?:if|elseif)\s+(\w+)\s*==\s*(\d+)\s+then\s*$', lines[i])
        if m and m.group(1) == var:
            ind, res = len(lines[i]) - len(lines[i].lstrip("\t ")), m.group(2)
            j, body = i + 1, []
            while j < len(lines):
                s = lines[j]
                if (len(s) - len(s.lstrip("\t "))) == ind and s.strip() in ("end", "else"):
                    break
                if (len(s) - len(s.lstrip("\t "))) == ind and s.strip().startswith(("elseif", "if ")):
                    break
                body.append(s)
                j += 1
            out.append((res, body))
            i = j
            continue
        i += 1
    return out

print("\n分歧剧本分支摘要:")
for sc in ["act2_3", "S0209_01_02", "ch1_2_2"]:
    if not os.path.exists(os.path.join(RAW, sc + ".txt")):
        continue
    t = open(os.path.join(RAW, sc + ".txt"), encoding="utf-8", errors="ignore").read()
    var = re.search(r'local\s+(\w+)\s*=\s*checkpointmanager\.Switch\("Combat_Result_01"\)', t)
    if not var:
        continue
    print("\n==", sc, "var", var.group(1))
    for res, body in blocks_of(sc, var.group(1)):
        keep = [x.strip() for x in body if re.search(r'SetNextScript|SetCurrentStoryScript|ChangeScene|Player\("life"', x)]
        print("   res%s: %s" % (res, " | ".join(keep[:4])[:180]))
