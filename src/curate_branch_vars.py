# -*- coding: utf-8 -*-
"""把页面里裸露的剧本变量换成人话（含被截断的残片、下划线写法）。

  switch1_3_result / switch_003_result / switch1_3_resul → 本场第 3 个判定
  choice_dice_001 / choice_dice1_2                       → 第 1 次掷骰 / 第 2 次掷骰
  choice_option_002 / choice_option1_4                   → 第 2 个选项 / 第 4 个选项
  X == N / X = N                                         → 前半句「…为 N」
条件类页面（type=条件）不改，那里要保留原始变量名。
跑在 curate_cond_explain.py 之后。"""
import sqlite3, json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
SWM = os.path.join(BASE, 'data', 'switch_map.json')
LIB = os.path.join(BASE, 'data', 'cond_lib.json')

SW = json.load(open(SWM, encoding='utf-8')) if os.path.exists(SWM) else {}
LIB = json.load(open(LIB, encoding='utf-8')) if os.path.exists(LIB) else {}

# 变量本身（含被截断的写法）
SWVAR = re.compile(r'switch\d*_(\d+)_?(?:resul?t?)?')
DICE = re.compile(r'choice_dice_?(\d+)_?(\d+)?')
OPT = re.compile(r'choice_option_?(\d+)_?(\d+)?')
JUDGE = re.compile(r'判定_(\d+)_?(?:resul?t?)?')
# 带比较的整段：X == N 或 X = N
CMP = re.compile(r'(switch\d*_\d+_?(?:resul?t?)?|choice_dice_?\d+_?\d*|choice_option_?\d+_?\d*|判定_\d+_?(?:resul?t?)?)\s*==?\s*(-?\d+)')

db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()


def cond_text(cid):
    a = (LIB.get(cid) or {}).get('attrs') or []
    return a[0] if a else ''


def human(script, text):
    smap = SW.get(script) or {}

    def _cmp(m):
        name, val = m.group(1), m.group(2)
        if name.startswith('switch'):
            n = str(int(SWVAR.search(name).group(1)))
            cid = ((smap.get(name) or {}).get('id')) or ''
            if not cid:
                for k, v in smap.items():
                    if k.rstrip('_result').rstrip('_') == name.rstrip('_result').rstrip('_'):
                        cid = v.get('id') or ''
                        break
            if cid:
                ct = cond_text(cid)
                return '第 %s 个判定（%s%s）为 %s' % (n, cid, ('：' + ct) if ct else '', val)
            return '第 %s 个判定为 %s' % (n, val)
        d = DICE.search(name)
        if d:
            idx = d.group(2) or d.group(1)
            return '第 %d 次掷骰为 %s' % (int(idx), val)
        o = OPT.search(name)
        if o:
            idx = o.group(2) or o.group(1)
            return '第 %d 个选项为 %s' % (int(idx), val)
        j = JUDGE.search(name)
        if j:
            return '第 %d 个判定为 %s' % (int(j.group(1)), val)
        return m.group(0)

    text = CMP.sub(_cmp, text)
    text = SWVAR.sub(lambda m: '第 %d 个判定' % int(m.group(1)), text)
    text = DICE.sub(lambda m: '第 %d 次掷骰' % int(m.group(2) or m.group(1)), text)
    text = OPT.sub(lambda m: '第 %d 个选项' % int(m.group(2) or m.group(1)), text)
    text = JUDGE.sub(lambda m: '第 %d 个判定' % int(m.group(1)), text)
    # 残留的裸写法（截断成没有序号的）
    text = re.sub(r'choice_dice[A-Za-z0-9_]*', '掷骰结果', text)
    text = re.sub(r'choice_option[A-Za-z0-9_]*', '选项结果', text)
    text = re.sub(r'switch\d*_\d+[A-Za-z0-9_]*', '判定结果', text)
    text = re.sub(r'switch[A-Za-z0-9_]*', '判定结果', text)
    return text


n_pages = n_rows = 0
q = ("select slug,type,lead,sections from pages where type<>'条件' and "
     "(lead like '%switch%' or lead like '%choice_dice%' or lead like '%choice_option%' or lead like '%判定_%' "
     "or sections like '%switch%' or sections like '%choice_dice%' or sections like '%choice_option%' or sections like '%判定_%')")
for r in list(c.execute(q)):
    script = r['slug'].split('/', 1)[1] if r['slug'].startswith('场景/') else ''
    lead = r['lead'] or ''
    new_lead = human(script, lead) if any(k in lead for k in ('switch', 'choice_dice', 'choice_option', '判定_')) else lead
    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        continue
    changed = 0
    for s in secs:
        for row in (s.get('rows') or []):
            for k in ('note', 'quote', 'label', 'title'):
                v = row.get(k)
                if not isinstance(v, str):
                    continue
                if any(x in v for x in ('switch', 'choice_dice', 'choice_option', '判定_')):
                    nv = human(script, v)
                    if nv != v:
                        row[k] = nv
                        changed += 1
        if isinstance(s.get('html'), str) and any(x in s['html'] for x in ('switch', 'choice_dice', 'choice_option')):
            s['html'] = human(script, s['html'])
            changed += 1
    if changed or new_lead != lead:
        c.execute("update pages set lead=?, sections=? where slug=?",
                  (new_lead, json.dumps(secs, ensure_ascii=False), r['slug']))
        n_pages += 1
        n_rows += changed

db.commit()
print('变量人话化：%d 页，%d 处' % (n_pages, n_rows))
