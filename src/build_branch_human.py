# -*- coding: utf-8 -*-
"""把剧本里的分支串翻成人话，供前端台词页直接显示。

  switch1_2_result=1 > switch1_3_result=1
    → 第2个判定（M40020_01：卧云岗回程结果1.被金乌上人敲头 2.被申屠龙吸内力 需=1）＝1
      → 再判第3个判定（…）＝1

  「继续考虑｜掷骰其他 > switch1_1_result=1」
    → 继续考虑（掷骰其他）→ 第1个判定（…）＝1

产物 data/branch_human.json，键为 "script\\x1f原文"。
"""
import sqlite3, json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
SW = json.load(open(os.path.join(BASE, 'data', 'switch_map.json'), encoding='utf-8'))
LIB = json.load(open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8'))

SWVAR = re.compile(r'switch\d*_(\d+)_?(?:resul?t?)?')
CMP = re.compile(r'(switch\d*_\d+_?(?:resul?t?)?)\s*==?\s*(-?\d+)')
DICE = re.compile(r'^(.*?)[｜|]\s*掷骰\s*(.+)$')
DICECMP = re.compile(r'choice_dice_?(\d+)_?(\d+)?\s*==?\s*(-?\d+)')
OPTCMP = re.compile(r'choice_option_?(\d+)_?(\d+)?\s*==?\s*(-?\d+)')
CONDREF = re.compile(r'条件\s+([A-Za-z0-9_]+)\s*[｜|]\s*(.+)')


def cond_text(cid):
    a = (LIB.get(cid) or {}).get('attrs') or []
    return a[0] if a else ''


def _switch(name, smap):
    n = int(SWVAR.search(name).group(1))
    cid = ((smap.get(name) or {}).get('id')) or ''
    if not cid:
        base = name.rstrip('_result').rstrip('_')
        for k, v in smap.items():
            if k.rstrip('_result').rstrip('_') == base:
                cid = v.get('id') or ''
                break
    ct = cond_text(cid) if cid else ''
    if cid and ct:
        return '第%d个判定（%s：%s）' % (n, cid, ct)
    if cid:
        return '第%d个判定（%s）' % (n, cid)
    return '第%d个判定' % n


def human_part(script, part):
    smap = SW.get(script) or {}
    # 条件 ID｜条件原文 → 【条件 ID】原文
    m = CONDREF.match(part)
    if m:
        return '【条件 %s】%s' % (m.group(1), m.group(2).strip())
    # 选项文案｜掷骰xx
    m = DICE.match(part)
    if m:
        return '%s（掷骰%s）' % (m.group(1).strip(), m.group(2).strip())
    if 'choice_dice' in part or 'choice_option' in part:
        part = DICECMP.sub(lambda mm: '第%s次掷骰＝%s' % (mm.group(2) or mm.group(1), mm.group(3)), part)
        part = OPTCMP.sub(lambda mm: '第%s个选项＝%s' % (mm.group(2) or mm.group(1), mm.group(3)), part)
        part = re.sub(r'choice_dice[A-Za-z0-9_]*', '掷骰结果', part)
        part = re.sub(r'choice_option[A-Za-z0-9_]*', '选项结果', part)
    if 'switch' in part:
        def _c(mm):
            return _switch(mm.group(1), smap) + '＝' + mm.group(2)
        out = CMP.sub(_c, part)
        if 'switch' in out:  # 没有 =值 的残留
            out = SWVAR.sub(lambda mm: _switch(mm.group(0), smap), out)
        return out
    return part


def human(script, text):
    parts = [p.strip() for p in str(text).split(' > ') if p.strip()]
    out = [human_part(script, p) for p in parts]
    return ' › '.join(out) if len(out) > 1 else (out[0] if out else '')


db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
pairs = set()
for (sc, b) in db.execute("select script,branch from branches where branch<>''"):
    pairs.add((sc, b))
for (sc, b) in db.execute("select script,branch from lines where branch<>''"):
    pairs.add((sc, b))
for (sc, b) in db.execute("select script,branch from flags where branch<>''"):
    pairs.add((sc, b))
for (sc, cd) in db.execute("select src,cond from scene_edges where cond<>''"):
    pairs.add((sc, cd))

out = {}
for sc, b in pairs:
    if not re.search(r'[A-Za-z]', b):
        continue
    h = human(sc, b)
    if h and h != b:
        out[sc + '\x1f' + b] = h

json.dump(out, open(os.path.join(BASE, 'data', 'branch_human.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
print('分支串人话 %d 条（共 %d 对）' % (len(out), len(pairs)))
