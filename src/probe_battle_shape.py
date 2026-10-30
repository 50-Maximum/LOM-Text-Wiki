# -*- coding: utf-8 -*-
"""诊断战斗分支的写法分布：elseif / else / 单支，决定解析策略。"""
import io, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
SW = re.compile(r'local\s+(\w+)\s*=\s*checkpointmanager\.Switch\("((?:Combat|Battle)_Result_[^"]+)"\)')
ifre = re.compile(r'^(\s*)(?:if|elseif)\s+(\w+)\s*==\s*(\d+)\s+then\s*$')
elsere = re.compile(r'^(\s*)else\s*$')
stat = collections.Counter()
samples = collections.defaultdict(list)
for fn in os.listdir(RAW):
    if not fn.endswith(".txt"):
        continue
    sc = fn[:-4]
    lines = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read().splitlines()
    var = None
    has = False
    n_if = n_else = n_elseif = 0
    for ln in lines:
        m = SW.search(ln)
        if m:
            var, has = m.group(1), True
            continue
        if not has or not var:
            continue
        mi = ifre.match(ln)
        if mi and mi.group(2) == var:
            if mi.group(1) and ln.strip().startswith("elseif"):
                n_elseif += 1
            else:
                n_if += 1
        elif elsere.match(ln):
            n_else += 1
    if not has:
        continue
    if n_else:
        stat["有else"] += 1
        if len(samples["有else"]) < 5:
            samples["有else"].append((sc, n_if, n_elseif, n_else))
    elif n_if + n_elseif <= 1:
        stat["单支"] += 1
        if len(samples["单支"]) < 5:
            samples["单支"].append((sc, n_if, n_elseif))
    else:
        stat["多elseif"] += 1
        if len(samples["多elseif"]) < 5:
            samples["多elseif"].append((sc, n_if, n_elseif))
print("战斗结果开关剧本:", sum(stat.values()), dict(stat))
for k, v in samples.items():
    print("\n", k, v)
