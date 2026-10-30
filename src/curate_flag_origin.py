# -*- coding: utf-8 -*-
"""给每个旗标页补「怎么置成这个值」——写入点逐条列出（哪场、第几行、SetFlag 还是 AddFlag、置成几、当时说什么）。
没有写入点的，直说剧本里没有 SetFlag/AddFlag。跑在 curate_gloss.py 之后。"""
import sqlite3, json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
PREF = re.compile(r'^[（(](读剧本归纳|按写入现场自动归纳)[^）)]*[）)]\s*')
DROP = re.compile(r'^(写入点：|最近一层判定|同时结算|另有\s*\d+\s*处写它|剧本里有|剧本里没有|读取场景|2,147)')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
CTX = os.path.join(BASE, 'data', 'flag_write_ctx.json')
if not os.path.exists(CTX):
    print('无 flag_write_ctx.json，先跑 src/build_switch_map.py')
    sys.exit(0)

W = json.load(open(CTX, encoding='utf-8'))
LIB = {}
_cl = os.path.join(BASE, 'data', 'cond_lib.json')
if os.path.exists(_cl):
    LIB = json.load(open(_cl, encoding='utf-8'))
GLOSS = {}
_gl = os.path.join(BASE, 'data', 'flag_gloss.json')
if os.path.exists(_gl):
    GLOSS = json.load(open(_gl, encoding='utf-8'))
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()
titles = {r['script']: (r['title'] or r['script']) for r in c.execute("select script,title from scenes")}

def rows_for(flag):
    out = []
    for w in W.get(flag, []):
        t = titles.get(w['script']) or w['script']
        note = '%s 第 %d 行 %s＝%s' % (t, w['line'], w['op'], w['value'])
        out.append({'note': note, 'quote': (w.get('text') or '')[:110],
                    'script': w['script'], 'title': t, 'seq': 0, 'routes': []})
    return out

def _collect(secs):
    """从含义段里抽出：一句含义、证据行、名称免责行。其余重复小标题一律不取。"""
    meaning = ''
    evid = ''
    keep = []
    for s in secs:
        if s.get('h') not in ('含义判定', '含义推断'):
            continue
        for row in (s.get('rows') or []):
            n = (row.get('note') or '').strip()
            if not n:
                continue
            if n.startswith('人话：'):
                continue
            if n.startswith('依据：') or n.startswith('依据:'):
                evid = n.split('：', 1)[-1].split(':', 1)[-1].strip()
                continue
            if DROP.match(n):
                continue
            if n.startswith('暂称') or n.startswith('游戏名称表'):
                keep.append(row)
                continue
            n2 = PREF.sub('', n).strip()
            if len(n2) > len(meaning):
                meaning = n2
    return meaning, evid, keep

n_add = n_keep = 0
for r in list(c.execute("select slug,name,lead,sections from pages where type='数值'")):
    slug = r['slug']
    if not slug.startswith('数值/旗标_'):
        continue
    flag = slug.split('数值/旗标_', 1)[1]
    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        continue
    rows = rows_for(flag)
    _mean0, _evid0, _keep0 = _collect(secs)
    if rows:
        sec = {'h': '怎么置成这个值', 'rows': rows}
    else:
        _r0 = [{'note': '剧本里没有找到 SetFlag / AddFlag 写入点，这个值多由引擎、选项效果或存档写入，原文里查不到明确触发处。',
                'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]
        if _evid0:
            _r0[0]['note'] = '剧本里没有直接的 SetFlag / AddFlag 写入点，这个值多由引擎、选项效果或存档写入。' \
                             '已知的线索：%s。' % _evid0
        sec = {'h': '怎么置成这个值', 'rows': _r0}
    # 一句含义，写进页首那句；下面不再另开一段重复说一遍
    _mean, _evid, _keep = _mean0, _evid0, _keep0
    _g = GLOSS.get(flag)
    _gt = ((_g.get('text') if isinstance(_g, dict) else (_g or '')) if _g else '').strip()
    if _gt and (not _mean or len(_gt) >= len(_mean) * 0.6):
        _mean = _gt
    _absorbed = False
    if _mean:
        _m = re.match(r'^(.*?剧本里(?:共\s*\d+\s*个判定读它[^。]*|没有判定读它)。)', r['lead'] or '')
        if _m:
            _newlead = _m.group(1) + _mean.rstrip('。') + '。'
            secs = [s for s in secs if s.get('h') not in ('含义判定', '含义推断')]
            if _keep:
                secs.insert(0, {'h': '名称说明', 'rows': _keep})
            _absorbed = True
            if _newlead != (r['lead'] or ''):
                c.execute("update pages set lead=? where slug=?", (_newlead, slug))
    if not _absorbed:
        # 页首没有可挂的计数句，就在段里留一句，不删
        secs = [s for s in secs if s.get('h') not in ('含义判定', '含义推断')]
        if _mean:
            secs.insert(0, {'h': '含义判定', 'rows': [
                {'note': _mean, 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}]})

    idx = None
    for i, s in enumerate(secs):
        if s.get('h') == '怎么置成这个值':
            idx = i
            break
    if idx is None:
        # 放在「含义判定」之后，没有就放最前
        pos = 0
        for i, s in enumerate(secs):
            if s.get('h') in ('含义判定', '含义推断'):
                pos = i + 1
                break
        secs.insert(pos, sec)
        n_add += 1
    else:
        secs[idx] = sec
        n_keep += 1
    c.execute("update pages set sections=? where slug=?",
              (json.dumps(secs, ensure_ascii=False), slug))
    # 相关条件那一团：光给编号没用，后面接上条件原文
    _fixed_cond = 0
    for s in secs:
        if not (s.get('h') or '').startswith('相关条件'):
            continue
        for row in (s.get('rows') or []):
            t = row.get('title') or ''
            if not t or '｜' in (row.get('note') or ''):
                continue
            a = (LIB.get(t) or {}).get('attrs') or []
            if a:
                row['note'] = '%s｜%s' % (t, a[0])
                _fixed_cond += 1
        if _fixed_cond:
            c.execute("update pages set sections=? where slug=?",
                      (json.dumps(secs, ensure_ascii=False), slug))

db.commit()
print('补写入点 %d 页，更新 %d 页' % (n_add, n_keep))
