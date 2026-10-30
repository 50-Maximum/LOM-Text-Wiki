# -*- coding: utf-8 -*-
"""补全所有被判定使用的数值与旗标条目：没建页的一律建出来，归到「数值」类。"""
import sqlite3, json, io, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()
DRY = '--dry' in sys.argv

conds = json.load(io.open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8'))
flags = json.load(io.open(os.path.join(BASE, 'data', 'flag_names.json'), encoding='utf-8'))
try:
    INFER = json.load(io.open(os.path.join(BASE, 'data', 'flag_infer.json'), encoding='utf-8'))
except Exception:
    INFER = {}
# 同一名字被多个旗标共用 → 说明官方表里给的是通用占位名，不能当成专名展示
_nr = {}
for _k, _v in flags.items():
    _nr.setdefault(_v, []).append(_k)
DUPNAME = {_v for _v, _ks in _nr.items() if len(_ks) > 1}
scenes_title = {r['script']: (r['title'] or r['script'])
                for r in c.execute("select script,title from scenes")}
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

LEFT = re.compile(r'^\s*([^\s≤≥＜＞=<>（）()]+)\s*(?:需)?\s*[≤≥＜＞=<>]')
FLAGID = re.compile(r'^(?:[A-Z]\d{4,}|B\d{5}|C\d{5}|Facility_\d+|TalkOption_\d+|Door_Free_\d+|Meeting_Option_|Ch_\d.*Break|Alpha_\d+|成就_\d+)')
use = collections.defaultdict(lambda: {'conds': [], 'forms': []})
for cid, v in conds.items():
    for a in (v.get('attrs') or []):
        m = LEFT.match(a)
        if not m:
            continue
        nm = m.group(1)
        if '(' in nm:
            continue
        use[nm]['conds'].append(cid)
        if a not in use[nm]['forms']:
            use[nm]['forms'].append(a)

have = {r[0] for r in c.execute("select slug from pages")}
made_s = made_f = 0
new_rows = []

def disp(nm):
    for p in ('好感度_', '技能_', '数值_', '贵重品_', '书籍_', '秘笈等级_', '杂物_', '成就_'):
        if nm.startswith(p):
            return nm[len(p):] + ('好感' if p == '好感度_' else '')
    return nm

for nm, rec in use.items():
    cl = sorted(set(rec['conds']))
    scs = []
    for cid in cl:
        for s in cond_scenes.get(cid) or []:
            if s not in scs:
                scs.append(s)
    is_flag = bool(FLAGID.match(nm)) or nm in flags
    if is_flag:
        slug = '数值/旗标_' + nm
        _inf = INFER.get(nm) or {}
        fname = flags.get(nm) or ''
        if slug in have and not _inf and fname not in DUPNAME:
            continue
        if fname and fname in DUPNAME:
            name = '旗标 %s（表内占位名：%s）' % (nm, fname)
        elif fname and fname != nm:
            name = '旗标 %s（%s）' % (nm, fname)
        else:
            name = '旗标 %s' % nm
        lead = ('旗标 %s%s：剧本里共 %d 个判定读它，牵涉 %d 个场景。'
                % (nm, ('（%s）' % fname) if fname and fname not in DUPNAME else '', len(cl), len(scs)))
        if _inf.get('note'):
            lead += _inf['note']
        kind, facet = '旗标', '旗标'
        made_f += 1
    else:
        # 非旗标：只给好感度 / 技能建页；其余左值属于官方 Stat 表的范畴，交给 curate_tables 处理
        if not (nm.startswith('好感度_') or nm.startswith('技能_')):
            continue
        slug = '数值/' + nm
        if slug in have:
            continue
        name = disp(nm)
        reqs = collections.Counter(rec['forms'])
        lead = '%s在剧本中共有 %d 处判定，最常见的门槛是%s。' % (
            name, len(cl), '、'.join(x for x, _ in reqs.most_common(3)) or '—')
        kind = '属性'
        facet = ('好感' if nm.startswith('好感度_') else '技能' if nm.startswith('技能_') else '属性')
        made_s += 1
    secs = []
    if is_flag and _inf:
        _r = [{'note': _inf.get('note') or '', 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]
        if _inf.get('ev'):
            _r.append({'note': '依据：' + _inf['ev'], 'quote': '', 'script': '', 'title': '',
                       'seq': 0, 'routes': []})
        secs.append({'h': '含义判定', 'rows': _r})
    if rec['forms']:
        secs.append({'h': '判定里怎么写的', 'rows': [
            {'note': a, 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}
            for a in rec['forms'][:20]]})
    if cl:
        secs.append({'h': '相关条件（%d 个）' % len(cl), 'rows': [
            {'note': cid, 'quote': '', 'script': '', 'title': cid, 'seq': 0, 'routes': []}
            for cid in cl[:40]]})
    if scs:
        secs.append({'h': '涉及场景（%d 个）' % len(scs), 'rows': [
            {'note': scenes_title.get(s, s), 'quote': '', 'script': s,
             'title': scenes_title.get(s, s), 'seq': 0, 'routes': []}
            for s in scs[:40]]})
    if not DRY:
        c.execute("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (slug, '数值', name, lead,
                   json.dumps({'类型': kind, '判定数': str(len(cl)), '场景数': str(len(scs))},
                              ensure_ascii=False),
                   json.dumps(secs, ensure_ascii=False),
                   json.dumps(['数值', facet], ensure_ascii=False), len(scs), '[]', nm,
                   '', 0, facet, (nm[:1] if is_flag else '')))
        for cid in cl[:60]:
            if '条件/' + cid in have:
                c.execute("insert or replace into links values(?,?,?,?)", (slug, '条件/' + cid, '相关条件', ''))
    new_rows.append((len(cl), name, slug))

if not DRY:
    # 把新条目补进「数值/总览」
    r = c.execute("select sections from pages where slug='数值/总览'").fetchone()
    if r:
        secs = json.loads(r[0] or '[]')
        for s in secs:
            if s.get('h') == '全部数值':
                have_notes = {x.get('note') for x in (s.get('rows') or [])}
                for n, name, slug in new_rows:
                    t = '%s（%d 处）' % (name, n)
                    if t not in have_notes:
                        s['rows'].append({'note': t, 'quote': '', 'script': '', 'title': '',
                                          'seq': 0, 'routes': []})
        c.execute("update pages set sections=? where slug='数值/总览'",
                  (json.dumps(secs, ensure_ascii=False),))
    c.execute("delete from links where src=dst")
    db.commit()
print('新增数值 %d 个、旗标 %d 个' % (made_s, made_f))
