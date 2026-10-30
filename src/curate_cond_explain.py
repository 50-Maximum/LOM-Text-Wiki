# -*- coding: utf-8 -*-
"""给条件页（判定）补两段：
  这是什么   —— 剧本里的检查点，按结果值选台词/去向；附条件原文
  结果对应什么 —— 每个结果值在各场里紧接着说了什么
跑在 curate_gloss.py 之后。"""
import sqlite3, json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
RESP = os.path.join(BASE, 'data', 'checkpoint_res.json')
SWM = os.path.join(BASE, 'data', 'switch_map.json')
COND = os.path.join(BASE, 'data', 'cond_lib.json')

RES = json.load(open(RESP, encoding='utf-8')) if os.path.exists(RESP) else {}
SW = json.load(open(SWM, encoding='utf-8')) if os.path.exists(SWM) else {}
LIB = json.load(open(COND, encoding='utf-8')) if os.path.exists(COND) else {}

db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()
titles = {r['script']: (r['title'] or r['script']) for r in c.execute("select script,title from scenes")}

# 判定 id 被哪些剧本调用（从 switch_map 反查）
used_in = {}
for sc, m in SW.items():
    for var, v in (m or {}).items():
        used_in.setdefault(v.get('id'), []).append({'script': sc, 'var': var, 'line': v.get('line')})

n = 0
for r in list(c.execute("select slug,name,lead,sections from pages where type='条件'")):
    cid = r['name']
    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        continue
    attrs = (LIB.get(cid) or {}).get('attrs') or []
    expr = '；'.join(attrs) if attrs else (r['lead'] or '').split('：', 1)[-1]

    res_rows = []
    _seen_res = {}
    for x in (RES.get(cid) or []):
        key = (x['script'], x['res'])
        txt = (x.get('text') or '').strip()
        if key in _seen_res:
            if txt and not _seen_res[key]:
                _seen_res[key] = txt
            continue
        _seen_res[key] = txt
    for (script, res), txt in _seen_res.items():
        t = titles.get(script) or script
        note = '%s：结果 %d → %s' % (t, res, txt or '（该结果下没有独立台词）')
        res_rows.append({'note': note, 'quote': '', 'script': script, 'title': t,
                         'seq': 0, 'routes': []})
    uniq = res_rows[:40]

    acts = used_in.get(cid) or []
    if acts:
        explain = ('这是剧本里的检查点（checkpointmanager.Switch）。剧本在这一步按结果值分岔：'
                   '结果不同，接下来放的台词、走的去向也不同。条件原文：%s。' % expr)
    else:
        par = []
        for s in secs:
            if s.get('h') in ('用到这个判定的场景', '引用场景'):
                par = [x.get('note') for x in (s.get('rows') or [])][:5]
        explain = ('这是场景的进入条件：条件满足才会进对应场景，不满足则走别的路。条件原文：%s。' % expr)
        if par:
            explain += '目前挂在：%s。' % '、'.join(par)

    new_secs = [{'h': '这是什么', 'rows': [
        {'note': explain, 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]}]
    if uniq:
        new_secs.append({'h': '结果对应什么', 'rows': uniq})
    if acts:
        _rows_act = []
        for a in acts[:30]:
            _v = a['var'] or ''
            _num = ''
            _parts = _v.split('_')
            for _p in _parts:
                if _p.isdigit():
                    _num = str(int(_p))
                    break
            _rows_act.append({
                'note': '%s 第 %s 行，第 %s 个判定' % (
                    titles.get(a['script']) or a['script'], a['line'], _num or '?'),
                'quote': '', 'script': a['script'], 'title': titles.get(a['script']) or a['script'],
                'seq': 0, 'routes': []})
        new_secs.append({'h': '剧本里在哪里判', 'rows': _rows_act})

    # 去掉同名旧段，插到最前
    secs = [s for s in secs if s.get('h') not in ('这是什么', '结果对应什么', '剧本里在哪里判')]
    secs = new_secs + secs
    c.execute("update pages set sections=? where slug=?", (json.dumps(secs, ensure_ascii=False), r['slug']))
    n += 1

db.commit()
print('条件页补说明 %d 页' % n)
