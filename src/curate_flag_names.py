# -*- coding: utf-8 -*-
"""统一旗标页的名字与计数口径：
- 名字：有官方名用官方名；没有且能取到像样的中文场景名，用「暂称」并注明；否则只留编号。
- 计数：一律用条件库扫描的值，避免正文与开头不一致。
"""
import sqlite3, json, io, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()

SF = json.load(io.open(os.path.join(BASE, 'data', 'scene_flags.json'), encoding='utf-8'))
CL = json.load(io.open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8'))
CU = json.load(io.open(os.path.join(BASE, 'data', 'cond_used.json'), encoding='utf-8'))
FLAGS = json.load(io.open(os.path.join(BASE, 'data', 'flag_names.json'), encoding='utf-8'))
try:
    _inf = json.load(io.open(os.path.join(BASE, 'data', 'flag_infer.json'), encoding='utf-8'))
except Exception:
    _inf = {}
HAND = {k for k, v in _inf.items() if not (v.get('note') or '').startswith('（按写入现场自动归纳')}

official = {}
for ln in io.open(os.path.join(BASE, 'data', 'raw', 'system', 'Flag_zh-cn.txt'),
                  encoding='utf-8-sig', errors='replace'):
    m = re.match(r'Flag/Name/(\S+)\s*=\s*(.+?)\s*$', ln)
    if m:
        official[m.group(1)] = m.group(2).strip()
NAME = dict(FLAGS)
NAME.update(official)
# 丢掉纯标点这类解析残留的名字
NAME = {k: v for k, v in NAME.items() if re.search(r'[\w\u4e00-\u9fff]', v or '')}
PH = re.compile(r'^(旗标暂存|决斗泛用事件旗标)\d+$')

TITLE = {r['script']: (r['title'] or r['script']) for r in c.execute("select script,title from scenes")}
writes = collections.defaultdict(list)
for sc, d in SF.items():
    for fid in (d.get('sets') or {}):
        writes[fid].append(sc)

FIDS = set(NAME) | set(writes)
for cid, v in CL.items():
    text = ' '.join((v.get('attrs') or [])) + ' ' + (v.get('expr') or '')
    for m in re.finditer(r'\(([A-Za-z0-9_]+)\)', text):
        FIDS.add(m.group(1))
    for m in re.finditer(r'([A-Za-z0-9_]+)\s*需', text):
        FIDS.add(m.group(1))
PATS = {f: re.compile(r'(?<![A-Za-z0-9_])' + re.escape(f) + r'(?![0-9])') for f in FIDS}
reads = collections.defaultdict(set)
for cid, v in CL.items():
    text = ' '.join((v.get('attrs') or [])) + ' ' + (v.get('expr') or '')
    for f, pat in PATS.items():
        if f in text and pat.search(text):
            reads[f].add(cid)


def counts(fid):
    ids = reads.get(fid) or set()
    scs = set()
    for cid in ids:
        for s in (CU.get(cid) or []):
            scs.add(s)
    return len(ids), len(scs)


CJK = re.compile(r'[\u4e00-\u9fff]')


def good(n):
    if not (n and CJK.search(n) and len(n) <= 18):
        return False
    if re.match(r'^[a-z0-9_]+$', n):
        return False
    for bad in ('你', '我', '这', '那', '・', '工作（', '接下来', '自由行动', '第一战'):
        if bad in n:
            return False
    return True


def nickname(fid):
    src = (writes.get(fid) or [''])[0]
    if not src:
        ids = sorted(reads.get(fid) or [])
        for cid in ids:
            if CU.get(cid):
                src = CU[cid][0]
                break
    t = re.sub(r'[（(].*?[)）]', '', TITLE.get(src, '') or '').strip()
    t = re.sub(r'\s+', '', t)[:14]
    return t if good(t) else ''


CLOSE = re.compile(r'^(剧本里共 \d+ 个判定读它(，牵涉 \d+ 个场景)?。|剧本里没有判定读它。)')

changed = 0
# 先算一遍可用的暂称；同一名字被多个旗标共用时（同一场戏里写了几个）一律不用，免得重名
_cand = {}
for _r in c.execute("select slug from pages where slug glob '数值/旗标_*'"):
    _fid = _r['slug'][len('数值/旗标_'):]
    _zh = NAME.get(_fid) or ''
    if _zh and not PH.match(_zh):
        continue
    _n = nickname(_fid)
    if _n:
        _cand.setdefault(_n, []).append(_fid)
EXCL = {fs[0]: nm for nm, fs in _cand.items() if len(fs) == 1}

for r in list(c.execute("select slug,name,lead,infobox,sections from pages where slug glob '数值/旗标_*'")):
    fid = r['slug'][len('数值/旗标_'):]
    ncl, nsc = counts(fid)
    zh = NAME.get(fid) or ''
    if zh and PH.match(zh):
        zh = ''
    nick = '' if zh else EXCL.get(fid, '')
    if zh:
        name = '旗标 %s（%s）' % (fid, zh)
    elif nick:
        name = '旗标 %s（暂称：%s）' % (fid, nick)
    else:
        name = '旗标 %s' % fid

    lead = r['lead'] or ''
    # 去掉开头的「旗标 xxx(...)：」与紧随的计数句，保留后面的描述
    body = re.sub(r'^旗标\s+\S+?\s*(（[^）]*）)*\s*[：:]', '', lead)
    body = CLOSE.sub('', body).strip()
    clause = ('剧本里共 %d 个判定读它' % ncl) + ('，牵涉 %d 个场景。' % nsc if nsc else '。') if ncl else '剧本里没有判定读它。'
    newlead = '旗标 %s%s：%s%s' % (
        fid, ('（%s）' % zh) if zh else (('（暂称：%s）' % nick) if nick else ''), clause, body)

    try:
        inf = json.loads(r['infobox'] or '{}')
    except Exception:
        inf = {}
    inf.pop('暂称', None)
    if zh:
        inf['官方名'] = zh
    else:
        inf.pop('官方名', None)
        if nick:
            inf['暂称'] = nick
    inf['判定数'] = str(ncl)

    if (name, newlead) != (r['name'], lead):
        c.execute("update pages set name=?, lead=?, infobox=? where slug=?",
                  (name, newlead, json.dumps(inf, ensure_ascii=False), r['slug']))
        changed += 1
db.commit()
print('统一 %d 页' % changed)
