# -*- coding: utf-8 -*-
"""给还没有「含义判定」的旗标页补一条位置说明。
有官方名就照抄；没有的，用「写入/读取它的那场戏的标题」拟一个暂称，并明确标注非官方。
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
INF = json.load(io.open(os.path.join(BASE, 'data', 'flag_infer.json'), encoding='utf-8'))

official = {}
p = os.path.join(BASE, 'data', 'raw', 'system', 'Flag_zh-cn.txt')
for ln in io.open(p, encoding='utf-8-sig', errors='replace'):
    m = re.match(r'Flag/Name/(\S+)\s*=\s*(.+?)\s*$', ln)
    if m:
        official[m.group(1)] = m.group(2).strip()
NAME = dict(FLAGS)
NAME.update(official)
PLACEHOLDER = re.compile(r'^(旗标暂存|决斗泛用事件旗标)\d+$')

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


def nice_title(t):
    t = re.sub(r'[（(].*?[)）]', '', t or '').strip()
    return t[:18]


done_named = done_invent = 0
ALL = list(c.execute("select slug,name,lead,sections,infobox from pages where slug glob '数值/旗标_*'"))
for r in ALL:
    fid = r['slug'][len('数值/旗标_'):]
    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        secs = []
    if any((s.get('h') or '') == '含义判定' for s in secs):
        continue
    ids = sorted(reads.get(fid) or [])
    scs = []
    for cid in ids:
        for s in (CU.get(cid) or []):
            if s not in scs:
                scs.append(s)
    wsc = writes.get(fid) or []
    zh = NAME.get(fid) or ''
    rows = []
    if zh and not PLACEHOLDER.match(zh):
        rows.append({'note': '游戏名称表写作「%s」。' % zh, 'quote': '', 'script': '', 'title': '',
                     'seq': 0, 'routes': []})
        done_named += 1
        nickname = ''
    else:
        src = (wsc[0] if wsc else (scs[0] if scs else ''))
        base = nice_title(TITLE.get(src, src)) if src else ''
        nickname = base or '未定'
        rows.append({'note': '游戏名称表没有给名字。暂称「%s」取自%s的那场戏「%s」，此名为本站拟名，不是游戏原文。'
                             % (nickname, '写入' if wsc else '读取', TITLE.get(src, src) or '—'),
                     'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
        done_invent += 1
    if ids:
        rows.append({'note': '剧本里有 %d 个判定读它：%s%s。' % (
            len(ids), '、'.join(ids[:4]), ' 等' if len(ids) > 4 else ''),
            'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
    else:
        rows.append({'note': '没有任何判定读它。', 'quote': '', 'script': '', 'title': '',
                     'seq': 0, 'routes': []})
    if scs:
        rows.append({'note': '读取它的场景（%d 个）：%s。' % (
            len(scs), '、'.join('「%s」' % TITLE.get(s, s) for s in scs[:4]) + (' 等' if len(scs) > 4 else '')),
            'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
    if wsc:
        rows.append({'note': '写入它的场景（%d 个）：%s。' % (
            len(wsc), '、'.join('「%s」' % TITLE.get(s, s) for s in wsc[:4]) + (' 等' if len(wsc) > 4 else '')),
            'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
    secs.insert(0, {'h': '含义判定', 'rows': rows})

    name = r['name']
    lead = r['lead']
    if nickname and nickname != '未定' and '暂称' not in name:
        name = '旗标 %s（暂称：%s）' % (fid, nickname)
        lead = re.sub(r'^旗标 %s' % re.escape(fid), name, lead)
    inf = json.loads(r['infobox'] or '{}')
    if nickname and nickname != '未定':
        inf['暂称'] = nickname
    c.execute("update pages set name=?, lead=?, sections=?, infobox=? where slug=?",
              (name, lead, json.dumps(secs, ensure_ascii=False),
               json.dumps(inf, ensure_ascii=False), r['slug']))

db.commit()
print('补说明：有官方名 %d 个、拟名 %d 个' % (done_named, done_invent))
