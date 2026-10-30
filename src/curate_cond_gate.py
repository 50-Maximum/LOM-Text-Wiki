# -*- coding: utf-8 -*-
"""给「进入条件」类条件页补两句实话：
   结果对应什么——只有满足/不满足两种，不满足就不进这些场景；
   剧本里在哪里判——挂在哪几场，属于进场判定，不在场内某一行。
多路判定（有 checkpoint 结果的）不动。
"""
import sqlite3, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()
RES = {}
_p = os.path.join(BASE, 'data', 'checkpoint_res.json')
if os.path.exists(_p):
    RES = json.load(open(_p, encoding='utf-8'))

n = 0
for r in list(c.execute("select slug,sections from pages where type='条件'")):
    cid = r['slug'].split('/', 1)[1]
    if cid in RES:
        continue
    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        continue
    hs = [s.get('h') for s in secs]
    if '结果对应什么' in hs or '剧本里在哪里判' in hs:
        continue
    scenes = []
    for s in secs:
        if s.get('h') == '用到这个判定的场景':
            for row in (s.get('rows') or []):
                t = row.get('title') or row.get('note') or ''
                if t and t not in scenes:
                    scenes.append(t)
    say = '这不是多路判定，只有两种结果：条件成立，就进入%s；不成立，就走别的路。' % (
        '、'.join('「%s」' % x for x in scenes[:4]) if scenes else '挂着它的场景')
    if len(scenes) > 4:
        say = say.replace('；不成立', ' 等 %d 场；不成立' % len(scenes))
    secs.insert(0, {'h': '这是什么', 'rows': [
        {'note': '这是场景的进入条件（不是 check→结果 的多路判定）。条件原文：%s。' % (
            ((json.load(open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8')).get(cid) or {}).get('attrs') or [''])[0]),
         'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]}) if '这是什么' not in hs else None
    secs = [s for s in secs if s is not None]
    hs = [s.get('h') for s in secs]
    add = [
        {'h': '结果对应什么', 'rows': [
            {'note': say, 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]},
        {'h': '剧本里在哪里判', 'rows': [
            {'note': '作为进场条件随场景加载时判定，不落在场内某一句台词上；挂在：%s。' % (
                '、'.join('「%s」' % x for x in scenes[:8]) if scenes else '（没有场景引用它）'),
             'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]},
    ]
    # 放在「判定内容」之前
    pos = len(secs)
    for i, s in enumerate(secs):
        if s.get('h') in ('判定内容', '用到这个判定的场景'):
            pos = i
            break
    secs[pos:pos] = add
    c.execute("update pages set sections=? where slug=?",
              (json.dumps(secs, ensure_ascii=False), r['slug']))
    n += 1

db.commit()
print('进入条件页补说明 %d 页' % n)
