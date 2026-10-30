# -*- coding: utf-8 -*-
"""把全部旗标建成可查的条目，归在「数值」类下。跑在 build 之后。"""
import sqlite3, json, io, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()
DRY = '--dry' in sys.argv

flags = json.load(io.open(os.path.join(BASE, 'data', 'flag_names.json'), encoding='utf-8'))
conds = json.load(io.open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8'))
try:
    INFER = json.load(io.open(os.path.join(BASE, 'data', 'flag_infer.json'), encoding='utf-8'))
except Exception:
    INFER = {}

# 条件 → 场景
cond_scenes = {}
for r in c.execute("select slug,sections from pages where type='条件'"):
    cid = r['slug'].split('/', 1)[1]
    got = []
    try:
        for s in json.loads(r['sections'] or '[]'):
            if (s.get('h') or '').startswith('用到这个判定的场景'):
                got = [x.get('script') for x in (s.get('rows') or []) if x.get('script')]
    except Exception:
        pass
    cond_scenes[cid] = got

IDPAT = re.compile(r'\(([A-Za-z][A-Za-z0-9_]*)\)')
flag_conds = collections.defaultdict(list)
flag_forms = collections.defaultdict(list)
for cid, v in conds.items():
    for a in (v.get('attrs') or []):
        for fid in set(IDPAT.findall(a)):
            if fid in flags:
                flag_conds[fid].append(cid)
                if a not in flag_forms[fid]:
                    flag_forms[fid].append(a)

scenes_title = {r['script']: (r['title'] or r['script'])
                for r in c.execute("select script,title from scenes")}
have = {r[0] for r in c.execute("select slug from pages")}

made = 0
rows_sum = []
for fid, fname in flags.items():
    cl = sorted(set(flag_conds.get(fid) or []))
    scs = []
    for cid in cl:
        for s in cond_scenes.get(cid) or []:
            if s not in scs:
                scs.append(s)
    _inf = INFER.get(fid) or {}
    if cl:
        lead = ('旗标 %s（%s）：剧本里共 %d 个判定读它，牵涉 %d 个场景。'
                % (fid, _inf.get('name') or fname, len(cl), len(scs)))
    else:
        lead = '旗标 %s（%s）：在剧本判定中没有被直接读取。' % (fid, _inf.get('name') or fname)
    if _inf.get('note'):
        lead += _inf['note']
    secs = []
    if _inf:
        _r = [{'note': _inf.get('note') or '', 'quote': '', 'script': '', 'title': '',
               'seq': 0, 'routes': []}]
        if _inf.get('ev'):
            _r.append({'note': '依据：' + _inf['ev'], 'quote': '', 'script': '', 'title': '',
                       'seq': 0, 'routes': []})
        secs.append({'h': '含义推断', 'rows': _r})
    if flag_forms.get(fid):
        secs.append({'h': '判定里怎么写的', 'rows': [
            {'note': a, 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}
            for a in flag_forms[fid][:20]]})
    if cl:
        secs.append({'h': '相关条件（%d 个）' % len(cl), 'rows': [
            {'note': cid, 'quote': '', 'script': '', 'title': cid, 'seq': 0, 'routes': []}
            for cid in cl[:40]]})
    if scs:
        secs.append({'h': '涉及场景（%d 个）' % len(scs), 'rows': [
            {'note': scenes_title.get(s, s), 'quote': '', 'script': s,
             'title': scenes_title.get(s, s), 'seq': 0, 'routes': []}
            for s in scs[:40]]})
    slug = '数值/旗标_' + fid
    name = ('旗标 %s（%s）' % (fid, _inf['name'])) if _inf.get('name') else (
        '旗标 %s（%s）' % (fid, fname) if fname and fname != fid else '旗标 %s' % fid)
    if not DRY:
        c.execute("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (slug, '数值', name, lead,
                   json.dumps({'类型': '旗标', '判定数': str(len(cl)), '场景数': str(len(scs))},
                              ensure_ascii=False),
                   json.dumps(secs, ensure_ascii=False),
                   json.dumps(['数值', '旗标'], ensure_ascii=False), len(scs), '[]', fid,
                   '', 0, '旗标', (fid[:1] if fid else '')))
        for cid in cl[:60]:
            tgt = '条件/' + cid
            if tgt in have:
                c.execute("insert or replace into links values(?,?,?,?)", (slug, tgt, '相关条件', ''))
        for s in scs[:20]:
            tgt = '场景/' + s
            if tgt in have:
                c.execute("insert or replace into links values(?,?,?,?)", (slug, tgt, '涉及场景', ''))
    made += 1
    rows_sum.append((len(cl), len(scs), fid, fname, slug))

rows_sum.sort(key=lambda x: (-x[0], -x[1], x[2]))
top = [{'note': '旗标 %s（%s）｜%d 个判定 / %d 个场景' % (f, n, a, b), 'quote': '',
        'script': '', 'title': '', 'seq': 0, 'routes': []} for a, b, f, n, s in rows_sum]
if not DRY:
    c.execute("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              ('数值/旗标总览', '数值', '旗标总览',
               '剧本里全部 %d 个旗标，按被判定读取的次数排序；每条都能点进单独条目，看它写在哪些判定、牵涉哪些场景。' % len(flags),
               json.dumps({'类型': '旗标总览', '条目': str(len(flags))}, ensure_ascii=False),
               json.dumps([{'h': '全部旗标', 'rows': top}], ensure_ascii=False),
               json.dumps(['数值', '旗标'], ensure_ascii=False), len(flags), '[]', '旗标总览',
               '', 0, '旗标', ''))
    for a, b, f, n, s in rows_sum[:120]:
        c.execute("insert or replace into links values(?,?,?,?)", ('数值/旗标总览', s, '旗标', ''))
    c.execute("delete from links where src=dst")
    db.commit()
print('旗标页 %d 个；有判定读取的 %d 个' % (made, sum(1 for x in rows_sum if x[0])))
