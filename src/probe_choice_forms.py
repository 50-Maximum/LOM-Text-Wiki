# -*- coding: utf-8 -*-
"""摸清选项定义的写法变体，为解析器定规则。"""
import io, sys, os, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
D = r"D:\LegendOfMortal Wiki\data\raw\scripts"
files = [f for f in os.listdir(D) if f.endswith(".txt")]
pat_block = re.compile(r"local\s+(option_\d+)\s*=\s*\{\}")
pat_assign = re.compile(r"^\s*(option_\d+)\[(\d+)\]\s*=\s*\"([^\"]+)\"")
pat_insert = re.compile(r"^\s*table\.insert\((\w+)")
pat_choose = re.compile(r"local\s+(\w+)\s*=\s*(?:choose|dicemenudialog\.\w+)\(")
pat_choose2 = re.compile(r"local\s+(\w+)\s*=\s*choose\(")
pat_dice = re.compile(r"dicemenudialog\.(\w+)")

cnt = collections.Counter()
cond_assign = 0
total_blocks = 0
examples = []
for f in files:
    lines = open(os.path.join(D, f), encoding="utf-8", errors="replace").read().split("\n")
    depth_if = 0
    in_block = False
    for i, ln in enumerate(lines):
        m = pat_block.search(ln)
        if m:
            in_block = True
            total_blocks += 1
            depth_if = 0
            cnt["block"] += 1
            if len(examples) < 3:
                examples.append((f, i + 1, ln.strip()))
            continue
        if in_block:
            s = ln.strip()
            if re.match(r"^if\s+.+then$", s):
                depth_if += 1
            elif s == "end":
                if depth_if > 0:
                    depth_if -= 1
            elif pat_assign.search(ln):
                if depth_if > 0:
                    cond_assign += 1
                    cnt["cond_assign"] += 1
                else:
                    cnt["plain_assign"] += 1
            elif pat_choose.search(ln) or pat_choose2.search(ln):
                cnt["choose"] += 1
                in_block = False
        for d in pat_dice.findall(ln):
            cnt["dice_" + d] += 1

print("选项块 %d，赋值 %d（其中条件赋值 %d），choose %d"
      % (total_blocks, cnt["plain_assign"] + cnt["cond_assign"], cond_assign, cnt["choose"]))
print("\n写法统计：")
for k, v in cnt.most_common(20):
    print("  %-22s %d" % (k, v))
print("\n样例：")
for e in examples:
    print("  %s:%d  %s" % e)
