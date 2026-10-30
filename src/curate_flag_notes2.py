# -*- coding: utf-8 -*-
"""把「只写位置」的旗标说明升级为「触发条件 + 位置 + 副作用」。
只动没有手写结论（flag_infer 里那条不以「（按写入现场自动归纳」开头）的页面。
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
SN = json.load(io.open(os.path.join(BASE, 'data', 'scene_next.json'), encoding='utf-8'))
FLAGS = json.load(io.open(os.path.join(BASE, 'data', 'flag_names.json'), encoding='utf-8'))
INF = json.load(io.open(os.path.join(BASE, 'data', 'flag_infer.json'), encoding='utf-8'))

HAND = {k for k, v in INF.items() if not (v.get('note') or '').startswith('（按写入现场自动归纳')}

official = {}
for ln in io.open(os.path.join(BASE, 'data', 'raw', 'system', 'Flag_zh-cn.txt'),
                  encoding='utf-8-sig', errors='replace'):
    m = re.match(r'Flag/Name/(\S+)\s*=\s*(.+?)\s*$', ln)
    if m:
        official[m.group(1)] = m.group(2).strip()
NAME = dict(FLAGS)
NAME.update(official)
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

_cache = {}


def scan(sc, fid):
    """返回 (行号, 值, 最近台词, 最近一层判定原文, 副作用列表)。"""
    key = (sc, fid)
    if key in _cache:
        return _cache[key]
    sp = os.path.join(BASE, 'data', 'raw', 'scripts', sc + '.txt')
    res = None
    if os.path.exists(sp):
        lines = io.open(sp, encoding='utf-8', errors='replace').read().splitlines()
        pat = re.compile(r'SetFlag\(\s*"' + re.escape(fid) + r'"\s*,\s*(-?\d+)')
        story = {}
        for p in (os.path.join(BASE, 'data', 'raw', 'story'),):
            pass
        for i, s in enumerate(lines):
            m = pat.search(s)
            if not m:
                continue
            last = ''
            for j in range(i, max(-1, i - 60), -1):
                mm = re.search(r'GetStoryText\("([^"]+)"\)', lines[j])
                if mm:
                    last = mm.group(1)
                    break
            cond = ''
            neg = False
            depth = 0
            for j in range(i - 1, max(-1, i - 500), -1):
                t = lines[j].strip()
                if not t or t.startswith('--'):
                    continue
                if re.match(r'^end\b', t):
                    depth += 1
                elif re.match(r'^else\b', t):
                    if depth == 0:
                        neg = True
                elif re.match(r'^(if|elseif)\b', t):
                    if depth == 0:
                        if ('==' in t) or ('result' in t) or ('choice' in t):
                            cond = ('不成立分支：' if (neg and t.startswith('if')) else '') + t
                            break
                    else:
                        depth -= 1
            side = []
            for j in range(max(0, i - 4), min(len(lines), i + 8)):
                mm = re.search(r'statmodifymanager\.(Player|AddItem|AddStory|AddFlag)\(\s*"?([^",)]*)', lines[j])
                if mm and 'SetFlag' not in lines[j]:
                    side.append('%s(%s)' % (mm.group(1), mm.group(2)))
            res = (i + 1, m.group(1), last, cond, side[:3])
            break
    _cache[key] = res
    return res


def cond_cn(script, condline):
    """把 if switch_00X_result == N 翻成条件中文（用 scene_next 的 label 映射）。"""
    if not condline:
        return ''
    neg = ''
    if condline.startswith('不成立分支：'):
        neg = '（else 分支，即下列条件不成立）'
        condline = condline[len('不成立分支：'):]
    m = re.match(r'(?:if|elseif)\s+(\w+)\s*==\s*(\d+)', condline)
    if not m:
        return (condline[:70] + neg)
    var, val = m.group(1), int(m.group(2))
    if var.startswith('choice'):
        return '选单第 %d 项%s' % (val, neg)
    labels = ((SN.get(script) or {}).get('labels') or {})
    cid = labels.get(var)
    if not cid:
        return '%s 取 %d%s' % (var, val, neg)
    attrs = ((CL.get(cid) or {}).get('attrs') or [])
    if 1 <= val <= len(attrs):
        return '%s 成立（%s）%s' % (cid, attrs[val - 1], neg)
    return '%s 取 %d%s' % (cid, val, neg)


def scene_next_line(sc, fid):
    """写这个旗标的那一行之后，下一处台词键（用来显示后果）。"""
    sp = os.path.join(BASE, 'data', 'raw', 'scripts', sc + '.txt')
    if not os.path.exists(sp):
        return ''
    lines = io.open(sp, encoding='utf-8', errors='replace').read().splitlines()
    pat = re.compile(r'SetFlag\(\s*"' + re.escape(fid) + r'"')
    for i, s in enumerate(lines):
        if pat.search(s):
            for j in range(i + 1, min(len(lines), i + 40)):
                mm = re.search(r'GetStoryText\("([^"]+)"\)', lines[j])
                if mm:
                    return mm.group(1)
            break
    return ''


done = 0
for r in list(c.execute("select slug,name,sections,infobox from pages where slug glob '数值/旗标_*'")):
    fid = r['slug'][len('数值/旗标_'):]
    if fid in HAND:
        continue
    ids = sorted(reads.get(fid) or [])
    scs = []
    for cid in ids:
        for s in (CU.get(cid) or []):
            if s not in scs:
                scs.append(s)
    wsc = writes.get(fid) or []
    zh = NAME.get(fid) or ''
    if zh and PH.match(zh):
        zh = ''
    rows = []
    nk = re.search(r'（暂称：([^）]+)）', r['name'] or '')
    row_nick = None
    if nk:
        row_nick = {'note': '暂称「%s」取自它所在的那场戏「%s」，是本站拟名，不是游戏原文。' % (
            nk.group(1), TITLE.get((wsc[0] if wsc else (scs[0] if scs else '')), '—')),
            'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}
    if zh:
        rows.append({'note': '游戏名称表写作「%s」。' % zh, 'quote': '', 'script': '', 'title': '',
                     'seq': 0, 'routes': []})
    elif wsc:
        rows.append({'note': '游戏名称表没有给名字，页面上用编号；下面的触发条件是照脚本读出来的，不是官方说明。',
                     'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
    else:
        rows.append({'note': '游戏名称表没有给名字，页面上用编号；脚本里没有写它的行。',
                     'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
    if row_nick:
        rows.append(row_nick)
    if wsc:
        sc = wsc[0]
        info = scan(sc, fid)
        if info:
            ln, val, lastkey, condline, side = info
            rows.append({'note': '写入点：「%s」（%s）第 %d 行，写入值 %s。' % (TITLE.get(sc, sc), sc, ln, val),
                         'quote': '', 'script': sc, 'title': TITLE.get(sc, sc), 'seq': 0, 'routes': []})
            cn = cond_cn(sc, condline)
            if cn:
                rows.append({'note': '最近一层判定：%s。' % cn, 'quote': '', 'script': '', 'title': '',
                             'seq': 0, 'routes': []})
            else:
                rows.append({'note': '前面没有分支判定，进入这场就写。', 'quote': '', 'script': '',
                             'title': '', 'seq': 0, 'routes': []})
            if side:
                rows.append({'note': '同时结算：%s。' % '、'.join(side), 'quote': '', 'script': '',
                             'title': '', 'seq': 0, 'routes': []})
        if len(wsc) > 1:
            rows.append({'note': '另有 %d 处写它：%s。' % (
                len(wsc) - 1, '、'.join('「%s」' % TITLE.get(s, s) for s in wsc[1:4])),
                'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
    if ids:
        rows.append({'note': '剧本里有 %d 个判定读它：%s%s。' % (
            len(ids), '、'.join(ids[:4]), ' 等' if len(ids) > 4 else ''),
            'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
        if scs:
            rows.append({'note': '读取场景：%s%s。' % (
                '、'.join('「%s」' % TITLE.get(s, s) for s in scs[:3]), ' 等' if len(scs) > 3 else ''),
                'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})
    else:
        if wsc:
            rows.append({'note': '2,147 个剧本里没有任何判定读它，属于只写不读的记录位。', 'quote': '',
                         'script': '', 'title': '', 'seq': 0, 'routes': []})
        else:
            rows.append({'note': '2,147 个剧本里既没有写它的行，也没有判定读它（应由游戏内系统写入）。',
                         'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []})

    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        secs = []
    secs = [s for s in secs if (s.get('h') or '') != '含义判定']
    secs.insert(0, {'h': '含义判定', 'rows': rows})
    # 同步重写开头段，去掉旧版自动说明的残留
    nick = ''
    if not zh:
        mm = re.search(r'（暂称：([^）]+)）', r['name'] or '')
        if mm:
            nick = mm.group(1)
    namepart = ('（%s）' % zh) if zh else (('（暂称：%s）' % nick) if nick else '')
    clause = ('剧本里共 %d 个判定读它' % len(ids)) + ('，牵涉 %d 个场景。' % len(scs) if scs else '。') \
        if ids else '剧本里没有判定读它。'
    lead = '旗标 %s%s：%s' % (fid, namepart, clause)
    c.execute("update pages set sections=?, lead=? where slug=?",
              (json.dumps(secs, ensure_ascii=False), lead, r['slug']))
    done += 1

db.commit()
print('升级说明 %d 页' % done)
