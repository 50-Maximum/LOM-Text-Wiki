# -*- coding: utf-8 -*-
"""给每个事件页补「判定与旗标」：这一幕牵涉的旗标读写、选项、属性条件。

数据来源：flags（写入）、choices（选项）、branch_nodes / scene_edges（读取的条件）、
flaginfo（旗标名）、cond_lib（条件原文）。
没有的一律写明「没有」，不留空。
"""
import sqlite3, json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()
LIB = json.load(open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8'))
FI = {r['flag']: r['label'] for r in c.execute("select flag,label from flaginfo")}


def ctext(cid):
    a = (LIB.get(cid) or {}).get('attrs') or []
    return a[0] if a else ''


def flag_name(f):
    lab = (FI.get(f) or '').strip()
    return '旗标 %s（%s）' % (f, lab) if lab and lab != f else '旗标 %s' % f


# 预取每个剧本的写入 / 选项 / 读取条件
W, O, R = {}, {}, {}
for r in c.execute("select script,seq,flag,value from flags"):
    W.setdefault(r['script'], []).append((r['seq'], r['flag'], r['value']))
for r in c.execute("select script,seq,checkpoint,options from choices"):
    try:
        opts = json.loads(r['options'] or '[]')
    except Exception:
        opts = []
    O.setdefault(r['script'], []).append((r['seq'], r['checkpoint'], opts))
for r in c.execute("select script,cond from branch_nodes where cond<>''"):
    for x in str(r['cond']).split('|'):
        x = x.strip()
        if x:
            R.setdefault(r['script'], set()).add(x)

n = 0
for r in list(c.execute("select slug,sections from pages where type='事件'")):
    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        continue
    scripts = []
    for s in secs:
        for row in (s.get('rows') or []):
            sc = row.get('script') or ''
            if sc and sc not in scripts:
                scripts.append(sc)
    rows = []
    for sc in scripts[:6]:
        for seq, f, v in W.get(sc, [])[:8]:
            rows.append({'note': '写入：%s＝%s（%s 第 %d 行）' % (flag_name(f), v, sc, seq),
                         'quote': '', 'script': sc, 'title': '', 'seq': 0, 'routes': []})
        for seq, cp, opts in O.get(sc, [])[:3]:
            if cp:
                t = ctext(cp)
                rows.append({'note': '选项判定「%s」%s（%s 第 %d 行）' % (
                    cp, ('：' + t) if t else '（脚本里只留了这个编号，没有条件原文）', sc, seq),
                    'quote': '', 'script': sc, 'title': '', 'seq': 0, 'routes': []})
            for op in opts[:4]:
                name = (op.get('text') or op.get('label') or op.get('key') or '').strip()
                if not name:
                    continue
                # 脚本内部指令（move+O_xxx+0+0 这类）不是台词，不往页面上放
                if re.match(r'^(move|event|jump|call|setflag|addflag)\+', name, re.I) or ('+' in name and len(name) > 18 and ' ' not in name):
                    continue
                # 纯英文/下划线的内部键（O_5_xxx、room_001_break_option 这类）不是台词
                if re.match(r'^[A-Za-z][A-Za-z0-9_]*$', name):
                    continue
                rows.append({'note': '选项：%s' % name[:60], 'quote': '',
                             'script': sc, 'title': '', 'seq': 0, 'routes': []})
        for cond in sorted(R.get(sc, set()))[:8]:
            t = ctext(cond)
            if t:
                rows.append({'note': '读取：%s（%s）' % (cond, t), 'quote': '',
                             'script': sc, 'title': '', 'seq': 0, 'routes': []})
    if not rows:
        rows = [{'note': '这一幕没有读写旗标，也没有选项或属性判定，按剧情顺序直接发生。',
                 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]
    # 去重
    seen, uniq = set(), []
    for x in rows:
        k = x['note']
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    secs = [s for s in secs if s.get('h') != '判定与旗标']
    secs.append({'h': '判定与旗标', 'rows': uniq[:40]})
    c.execute("update pages set sections=? where slug=?",
              (json.dumps(secs, ensure_ascii=False), r['slug']))
    n += 1

db.commit()
print('事件页补判定与旗标 %d 页' % n)
