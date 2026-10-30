# -*- coding: utf-8 -*-
"""把 data/flag_infer.json 的判定结论统一盖到旗标页上。
跑在 curate_flags / curate_numbers / curate_tables 之后，避免三方各写一套。
判定数/场景数沿用各页原本的统计，口径不跨页漂移。
"""
import sqlite3, json, io, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()

INFER = json.load(io.open(os.path.join(BASE, 'data', 'flag_infer.json'), encoding='utf-8'))
FLAGS = json.load(io.open(os.path.join(BASE, 'data', 'flag_names.json'), encoding='utf-8'))
CONDLIB = json.load(io.open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8'))
COND_USED = json.load(io.open(os.path.join(BASE, 'data', 'cond_used.json'), encoding='utf-8'))
SCENE_FLAGS = json.load(io.open(os.path.join(BASE, 'data', 'scene_flags.json'), encoding='utf-8'))

# 所有可能是旗标的编号：写入过的 + 名称表里的 + 条件里出现过的
FIDS = set(FLAGS)
for _sc, _d in SCENE_FLAGS.items():
    FIDS.update((_d.get('sets') or {}).keys())
for _cid, _v in CONDLIB.items():
    text = ' '.join((_v.get('attrs') or [])) + ' ' + (_v.get('expr') or '')
    for m in re.finditer(r'\(([A-Za-z0-9_]+)\)', text):
        FIDS.add(m.group(1))
    for m in re.finditer(r'([A-Za-z0-9_]+)\s*需', text):
        FIDS.add(m.group(1))
FIDS = sorted(FIDS, key=len, reverse=True)
_PAT = {f: re.compile(r'(?<![A-Za-z0-9_])' + re.escape(f) + r'(?![0-9])') for f in FIDS}

scan_reads = {}
for _fid, _pat in _PAT.items():
    ids = set()
    for _cid, _v in CONDLIB.items():
        text = ' '.join((_v.get('attrs') or [])) + ' ' + (_v.get('expr') or '')
        if _fid in text and _pat.search(text):
            ids.add(_cid)
    if ids:
        scan_reads[_fid] = ids

official = {}
p = os.path.join(BASE, 'data', 'raw', 'system', 'Flag_zh-cn.txt')
if os.path.exists(p):
    for ln in io.open(p, encoding='utf-8-sig', errors='replace'):
        m = re.match(r'Flag/Name/(\S+)\s*=\s*(.+?)\s*$', ln)
        if m:
            official[m.group(1)] = m.group(2).strip()
name_of = dict(FLAGS)
name_of.update(official)

# 只有「通用占位名」才算占位：同名的不同旗标若名字是势力名（丐帮、青城派）则是真名
PLACEHOLDER = re.compile(r'^(旗标暂存|决斗泛用事件旗标)\d+$')
NUM2 = re.compile(r'共\s*(\d+)\s*个判定读它[，,]?\s*牵涉\s*(\d+)\s*个场景')
NUM1 = re.compile(r'共\s*(\d+)\s*个判定读它')

created = 0
done = 0
for fid, rec in INFER.items():
    slug = '数值/旗标_' + fid
    zh = name_of.get(fid) or ''
    if zh and PLACEHOLDER.match(zh):
        name, namepart = '旗标 %s（表内占位名：%s）' % (fid, zh), ''
    elif zh and zh != fid:
        name, namepart = '旗标 %s（%s）' % (fid, zh), '（%s）' % zh
    else:
        name, namepart = '旗标 %s' % fid, ''

    row = c.execute("select lead,sections,infobox from pages where slug=?", (slug,)).fetchone()
    ncl = nsc = None
    if row:
        m = NUM2.search(row['lead'] or '')
        if m:
            ncl, nsc = int(m.group(1)), int(m.group(2))
        else:
            m = NUM1.search(row['lead'] or '')
            if m:
                ncl = int(m.group(1))
        if ncl is None:
            try:
                ncl = int((json.loads(row['infobox'] or '{}') or {}).get('判定数') or 0)
            except Exception:
                ncl = 0
    _sids = scan_reads.get(fid) or set()
    _ssc = set()
    for _c in _sids:
        for _x in (COND_USED.get(_c) or []):
            _ssc.add(_x)
    if not ncl:
        ncl = len(_sids)
    if not nsc:
        nsc = len(_ssc)
    if ncl:
        body = ('剧本里共 %d 个判定读它%s。'
                % (ncl, ('，牵涉 %d 个场景' % nsc) if nsc else ''))
    else:
        body = '剧本里没有判定读它。'
    lead = '旗标 %s%s：%s%s' % (fid, namepart, body, rec.get('note') or '')
    rows = [{'note': rec.get('note') or '', 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]
    if rec.get('ev'):
        rows.append({'note': '依据：' + rec['ev'], 'quote': '', 'script': '', 'title': '',
                     'seq': 0, 'routes': []})

    if not row:
        inf = {'类型': '旗标', '判定数': str(ncl)}
        if zh and not PLACEHOLDER.match(zh):
            inf['官方名'] = zh
        c.execute("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (slug, '数值', name, lead, json.dumps(inf, ensure_ascii=False),
                   json.dumps([{'h': '含义判定', 'rows': rows}], ensure_ascii=False),
                   json.dumps(['数值', '旗标'], ensure_ascii=False), nsc or 0, '[]', fid, '', 0,
                   '旗标', fid[:1]))
        created += 1
        continue
    try:
        secs = json.loads(row['sections'] or '[]')
    except Exception:
        secs = []
    secs = [s for s in secs if (s.get('h') or '') != '含义判定']
    secs.insert(0, {'h': '含义判定', 'rows': rows})
    try:
        inf = json.loads(row['infobox'] or '{}')
    except Exception:
        inf = {}
    if zh and not PLACEHOLDER.match(zh):
        inf['官方名'] = zh
    inf['判定数'] = str(ncl)
    c.execute("update pages set name=?, lead=?, sections=?, infobox=? where slug=?",
              (name, lead, json.dumps(secs, ensure_ascii=False),
               json.dumps(inf, ensure_ascii=False), slug))
    done += 1

db.commit()
print('覆盖 %d 个、新建 %d 个旗标页（推理库共 %d 条）' % (done, created, len(INFER)))
