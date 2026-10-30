# -*- coding: utf-8 -*-
"""按游戏自带名称表重建数值/旗标/设施条目，并清掉从条件字符串里臆造出来的条目。"""
import sqlite3, json, io, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()
DRY = '--dry' in sys.argv
SYS = os.path.join(BASE, 'data', 'raw', 'system')


def table(fn, pat):
    d = {}
    for ln in io.open(os.path.join(SYS, fn), encoding='utf-8', errors='replace'):
        m = re.match(pat, ln)
        if m:
            d[m.group(1)] = m.group(2).strip()
    return d


stats = table('Stat_zh-cn.txt', r'PlayerStat/(\S+)\s*=\s*(.+?)\s*$')
descs = table('Stat_zh-cn.txt', r'PlayerStatDesc/(\S+)\s*=\s*(.+?)\s*$')
tiers = collections.defaultdict(list)
for ln in io.open(os.path.join(SYS, 'Stat_zh-cn.txt'), encoding='utf-8', errors='replace'):
    m = re.match(r'StatLevel/([a-z]+)(\d+)\s*=\s*(.+?)\s*$', ln)
    if m:
        tiers[m.group(1)].append((int(m.group(2)), m.group(3).strip()))
for k in tiers:
    tiers[k].sort()

flags = table('Flag_zh-cn.txt', r'Flag/Name/(\S+)\s*=\s*(.+?)\s*$')
fac = table('Facility_zh-cn.txt', r'Facility/Name/(\d+)\s*=\s*(.+?)\s*$')
fac_eff = {}
for ln in io.open(os.path.join(SYS, 'Facility_zh-cn.txt'), encoding='utf-8', errors='replace'):
    m = re.match(r'Facility/Effect/(\d+)_1\s*=\s*(.+?)\s*$', ln)
    if m:
        fac_eff['Facility_' + m.group(1)] = m.group(2).strip()

cond_lib = json.load(io.open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8'))
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

scenes_title = {r['script']: (r['title'] or r['script'])
                for r in c.execute("select script,title from scenes")}
have = {r[0] for r in c.execute("select slug from pages")}

LEFT = re.compile(r'^\s*([^\s≤≥＜＞=<>（）()]+)\s*(?:需)?\s*[≤≥＜＞=<>]')
use = collections.defaultdict(lambda: {'conds': set(), 'forms': []})
for cid, v in cond_lib.items():
    for a in (v.get('attrs') or []):
        m = LEFT.match(a)
        if not m:
            continue
        nm = m.group(1)
        if '(' in nm:
            continue
        use[nm]['conds'].add(cid)
        if a not in use[nm]['forms']:
            use[nm]['forms'].append(a)

def page_for(slug, name, lead, inf, secs, facet, facet2='', sort=''):
    if DRY:
        return
    c.execute("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (slug, '数值', name, lead, json.dumps(inf, ensure_ascii=False),
               json.dumps(secs, ensure_ascii=False),
               json.dumps(['数值', facet], ensure_ascii=False), 0, '[]', sort, '', 0, facet, facet2))

# ---------- 1. 官方数值 ----------
made = 0
zh2key = {zh: k for k, zh in stats.items()}
for key, zh in stats.items():
    nm = zh
    rec = use.get(zh) or use.get(key) or {'conds': set(), 'forms': []}
    alt = [k for k in use if k.startswith(zh + '_') or k.endswith('_' + zh)]
    forms = list(rec['forms'])
    for k in alt:
        forms += use[k]['forms']
    cl = sorted(rec['conds'] | set().union(*[use[k]['conds'] for k in alt])) if alt else sorted(rec['conds'])
    scs = []
    for cid in cl:
        for s in cond_scenes.get(cid) or []:
            if s not in scs:
                scs.append(s)
    secs = []
    d = descs.get(key)
    if d:
        secs.append({'h': '官方说明', 'rows': [{'note': d, 'quote': '', 'script': '', 'title': '',
                                                 'seq': 0, 'routes': []}]})
    if key in tiers:
        secs.append({'h': '五档状态', 'rows': [
            {'note': '%d 档：%s' % (n, t), 'quote': '', 'script': '', 'title': '', 'seq': 0,
             'routes': []} for n, t in tiers[key]]})
    if forms:
        secs.append({'h': '判定里怎么写的', 'rows': [
            {'note': a, 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}
            for a in forms[:20]]})
    if cl:
        secs.append({'h': '相关条件（%d 个）' % len(cl), 'rows': [
            {'note': cid, 'quote': '', 'script': '', 'title': cid, 'seq': 0, 'routes': []}
            for cid in cl[:40]]})
    if scs:
        secs.append({'h': '涉及场景（%d 个）' % len(scs), 'rows': [
            {'note': scenes_title.get(s, s), 'quote': '', 'script': s,
             'title': scenes_title.get(s, s), 'seq': 0, 'routes': []}
            for s in scs[:40]]})
    lead = '%s：官方内部键 %s。%s' % (zh, key, d or '')
    if cl:
        lead += '剧本里 %d 个判定用到它。' % len(cl)
    page_for('数值/' + zh, nm, lead, {'类型': '数值', '内部键': key, '判定数': str(len(cl))},
             secs, '属性', '', key)
    made += 1
print('官方数值页 %d 个' % made)
if not DRY:
    for key in stats:
        c.execute("delete from pages where slug=? and type='数值'", ('数值/' + key,))
        c.execute("delete from links where src=? or dst=?", ('数值/' + key, '数值/' + key))

# ---------- 2. 官方旗标与设施 ----------
fm = 0
for fid, zh in flags.items():
    rec = use.get(fid) or {'conds': set(), 'forms': []}
    cl = sorted(rec['conds'])
    scs = []
    for cid in cl:
        for s in cond_scenes.get(cid) or []:
            if s not in scs:
                scs.append(s)
    secs = [{'h': '官方名称', 'rows': [{'note': '游戏名称表：%s' % zh, 'quote': '', 'script': '',
                                        'title': '', 'seq': 0, 'routes': []}]}]
    if rec['forms']:
        secs.append({'h': '判定里怎么写的', 'rows': [
            {'note': a, 'quote': '', 'script': '', 'title': '', 'seq': 0, 'routes': []}
            for a in rec['forms'][:20]]})
    if scs:
        secs.append({'h': '涉及场景（%d 个）' % len(scs), 'rows': [
            {'note': scenes_title.get(s, s), 'quote': '', 'script': s,
             'title': scenes_title.get(s, s), 'seq': 0, 'routes': []}
            for s in scs[:40]]})
    lead = '旗标 %s：游戏名称表写作「%s」。%s' % (
        fid, zh, ('剧本里 %d 个判定读它。' % len(cl)) if cl else '剧本判定里没有直接读它。')
    page_for('数值/旗标_' + fid, '旗标 %s（%s）' % (fid, zh), lead,
             {'类型': '旗标', '官方名': zh, '判定数': str(len(cl))}, secs, '旗标', fid[:1], fid)
    fm += 1
for n, zh in fac.items():
    fid = 'Facility_' + n
    rec = use.get(fid) or {'conds': set(), 'forms': []}
    cl = sorted(rec['conds'])
    scs = []
    for cid in cl:
        for s in cond_scenes.get(cid) or []:
            if s not in scs:
                scs.append(s)
    secs = [{'h': '官方名称', 'rows': [{'note': '设施 %s：%s' % (n, zh), 'quote': '', 'script': '',
                                        'title': '', 'seq': 0, 'routes': []}]}]
    if fac_eff.get(fid):
        secs.append({'h': '效果', 'rows': [{'note': fac_eff[fid], 'quote': '', 'script': '',
                                            'title': '', 'seq': 0, 'routes': []}]})
    if scs:
        secs.append({'h': '涉及场景（%d 个）' % len(scs), 'rows': [
            {'note': scenes_title.get(s, s), 'quote': '', 'script': s,
             'title': scenes_title.get(s, s), 'seq': 0, 'routes': []}
            for s in scs[:40]]})
    page_for('数值/旗标_' + fid, '设施 %s（%s）' % (n, zh),
             '设施 %s「%s」：建成后在大门选单里出现入口；未赎回时显示「尚未赎回」。' % (n, zh),
             {'类型': '设施', '编号': n}, secs, '旗标', 'F', fid)
    fm += 1
print('官方旗标/设施页 %d 个' % fm)

# ---------- 3. 清理臆造条目 ----------
JUNK = re.compile(r'^(Talk_|Door_|Guard_|P_Out_|\d+$|Ch_|Max_|S\d|M\d|A\d|BattleProgress|Alpha_|Z\d)|(\+|_向心力$|_轻功$|_暗器$|^南宫世家_锦香宫_上官世家$)')
removed = 0
for r in list(c.execute("select slug,name,facet from pages where type='数值'")):
    base = r['slug'].split('/', 1)[1]
    if r['slug'] in ('数值/总览', '数值/旗标总览'):
        continue
    if r['slug'].startswith('数值/旗标_'):
        continue
    if r['facet'] in ('好感', '技能'):
        continue
    if base in zh2key:
        continue
    removed += 1
    if not DRY:
        c.execute("delete from pages where slug=?", (r['slug'],))
        c.execute("delete from links where src=? or dst=?", (r['slug'], r['slug']))
print('清理非官方数值条目 %d 个' % removed)

if not DRY:
    c.execute("delete from links where src=dst")
    db.commit()
