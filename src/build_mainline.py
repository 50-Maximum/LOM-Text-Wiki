# -*- coding: utf-8 -*-
"""按「必经」重算主线：无条件接续 + 条件边目标唯一（玩家无选择）+ 战斗后推进。

输出 data/mainline_fix.json（script -> 主线/支线）
"""
import json, os, sys, collections

BASE = r'D:\LegendOfMortal Wiki'
D = lambda n: json.load(open(os.path.join(BASE, 'data', n), encoding='utf-8'))

nx = D('scene_next.json')          # src -> {next, edges:[{target,cond,kind}]}
scenes = D('story_segments.json')  # 只用 seg_of 判断哪些脚本存在
order = D('scene_order.json')

EDGES = {}
for src, d in nx.items():
    es = []
    if d.get('next'):
        es.append((d['next'], '', 'main'))
    for e in (d.get('edges') or []):
        t = e.get('target')
        if t:
            es.append((t, e.get('cond') or '', e.get('kind') or ''))
    EDGES[src] = es

HUBS = {'Free', 'Combat', 'Battle', 'Title', 'GameOver', 'Story', 'End'}


def is_main_step(es):
    """从本场出发，玩家没有选择的分支：返回必经目标列表。"""
    outs = []
    for t, c, k in es:
        if t in HUBS:
            continue
        outs.append((t, c))
    if not outs:
        return []
    # 去重
    tset = {t for t, _ in outs}
    if len(tset) == 1:
        return [list(tset)[0]]
    # 条件边目标唯一也算必经（无选项，只有判定）
    cond = [t for t, c in outs if c]
    if cond and len(set(cond)) == 1:
        return [cond[0]]
    return []


# 章节起点：没有入边的场景
inbound = collections.Counter()
for src, es in EDGES.items():
    for t, _c, _k in es:
        if t in nx:
            inbound[t] += 1

starts = [s for s in nx if inbound[s] == 0 and (s in nx)]
main = set()
stack = list(starts)
while stack:
    s = stack.pop()
    if s in main:
        continue
    main.add(s)
    for t in is_main_step(EDGES.get(s, [])):
        if t in nx and t not in main:
            stack.append(t)

# 只保留有台词的脚本
lines = json.load(open(os.path.join(BASE, 'data', 'manifest.json'), encoding='utf-8')) if os.path.exists(
    os.path.join(BASE, 'data', 'manifest.json')) else {}
allsc = set(nx)
main_dialogue = {s for s in main if (nx.get(s) or {}).get('edges') is not None}

out = {s: ('主线' if s in main else '支线') for s in allsc}
json.dump(out, open(os.path.join(BASE, 'data', 'mainline_fix.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)

from collections import Counter
print('场景总数', len(allsc), '主线', sum(1 for v in out.values() if v == '主线'),
      '支线', sum(1 for v in out.values() if v == '支线'))
print('起点数', len(starts), '示例', starts[:5])
