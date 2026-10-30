# -*- coding: utf-8 -*-
"""势力整理：合并、删除、改名、挂父子，重建「下辖势力」并同步人物筛选。"""
import sqlite3, json, io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
DRY = '--dry' in sys.argv
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()

MERGE = {'大理段氏': '大理', '岭南剑派': '岭南派', '阴曹': '地狱道'}
RENAME = {'赶山赶风寨': '赶风寨'}
DELETE = ['江陵谋逆', '正一道', '盐帮', '瑞家', '叶家', '龙家', '大铁铺']
PARENT = {
    '大理内戒营': '大理', '松烟阁': '大理',
    '岳家旧部': '朝廷', '清源侯府': '朝廷', '襄阳守军': '朝廷', '江陵厢军': '朝廷', '马军司': '朝廷',
    '方岳队': '风火义从', '疾风队': '风火义从', '风火义从': '崆峒派', '执明司': '崆峒派',
    '茂洲蕃部': '吐蕃', '地狱道': '泥教', '白风军': '极乐教',
}
NEW_FACTIONS = {
    '朝廷': ('政权', '宋室及其官署、军队与地方政务系统。江陵厢军、襄阳守军、马军司、清源侯府、'
             '岳家旧部皆隶其下。'),
}

fac = {r['name']: dict(r) for r in c.execute("select * from pages where type='势力'")}

def secs_of(r):
    try:
        return json.loads(r['sections'] or '[]')
    except Exception:
        return []

print('== 势力合并 ==')
for src, dst in MERGE.items():
    s, d = fac.get(src), fac.get(dst)
    if not s or not d:
        print('  缺页，跳过:', src, '->', dst)
        continue
    print('  %s -> %s' % (src, dst))
    if DRY:
        continue
    ds = secs_of(d)
    idx = {x.get('h'): x for x in ds}
    for sec in secs_of(s):
        h = sec.get('h') or ''
        if h.startswith('脚注') or h.startswith('下辖势力') or h.startswith('本派成员'):
            continue
        t = idx.get(h)
        if t is None:
            ds.append(sec)
            idx[h] = sec
        else:
            have = {(x.get('note'), x.get('script')) for x in (t.get('rows') or [])}
            for x in (sec.get('rows') or []):
                if (x.get('note'), x.get('script')) not in have:
                    t.setdefault('rows', []).append(x)
    c.execute("update pages set sections=? where slug=?", (json.dumps(ds, ensure_ascii=False), d['slug']))
    c.execute("insert or replace into aliases values(?,?)", (src, d['slug']))
    c.execute("update links set dst=? where dst=?", (d['slug'], s['slug']))
    c.execute("update links set src=? where src=?", (d['slug'], s['slug']))
    c.execute("delete from pages where slug=?", (s['slug'],))
    c.execute("update pages set facet=? where type='人物' and facet=?", (dst, src))
    fac.pop(src, None)

print('== 势力删除 ==')
for nm in DELETE:
    r = fac.get(nm)
    if not r:
        continue
    print('  删除', nm)
    if DRY:
        continue
    c.execute("delete from pages where slug=?", (r['slug'],))
    c.execute("delete from links where src=? or dst=?", (r['slug'], r['slug']))
    c.execute("update pages set facet='其他' where type='人物' and facet=?", (nm,))
    fac.pop(nm, None)

print('== 势力改名 ==')
for old, new in RENAME.items():
    r = fac.get(old)
    if not r:
        print('  缺页，跳过:', old)
        continue
    print('  %s -> %s' % (old, new))
    if not DRY:
        c.execute("update pages set name=? where slug=?", (new, r['slug']))
        c.execute("insert or replace into aliases values(?,?)", (new, r['slug']))
        c.execute("update pages set facet=? where type='人物' and facet=?", (new, old))

print('== 补建势力页 ==')
for nm, (kind, lead) in NEW_FACTIONS.items():
    if nm in fac:
        continue
    print('  新建', nm)
    if DRY:
        continue
    slug = '势力/' + nm
    c.execute("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (slug, '势力', nm, lead, json.dumps({'类型': kind, '名称': nm}, ensure_ascii=False),
               '[]', json.dumps(['势力', kind], ensure_ascii=False), 0, '[]', '', '', 0, kind, ''))

print('== 挂父子 ==')
for child, par in PARENT.items():
    print('  %s → %s' % (child, par))
    if DRY:
        continue
    r = fac.get(child)
    if r:
        inf = json.loads(r['infobox'] or '{}')
        inf['上级'] = par
        c.execute("update pages set infobox=? where slug=?",
                  (json.dumps(inf, ensure_ascii=False), r['slug']))
        c.execute("insert or replace into links values(?,?,?,?)", (r['slug'], '势力/' + par, '上级', par))

print('== 重建下辖势力 ==')
allrows = [dict(x) for x in c.execute("select * from pages where type='势力'")]
kids = {}
for ch, pa in PARENT.items():
    kids.setdefault(pa, []).append(ch)
for r in allrows:
    nm = r['name']
    secs = secs_of(r)
    base = set()
    for s in secs:
        if (s.get('h') or '').startswith('下辖势力'):
            for x in (s.get('rows') or []):
                if x.get('note'):
                    base.add(x['note'])
    lst = sorted(base | set(kids.get(nm) or []))
    secs = [s for s in secs if not (s.get('h') or '').startswith('下辖势力')]
    if lst:
        secs.append({'h': '下辖势力（%d 个）' % len(lst),
                     'rows': [{'note': x, 'quote': '', 'script': '', 'title': x, 'seq': 0,
                               'routes': []} for x in lst]})
        if not DRY:
            c.execute("update pages set sections=? where slug=?",
                      (json.dumps(secs, ensure_ascii=False), r['slug']))
        print('  %s: %d 个' % (nm, len(lst)))

if not DRY:
    c.execute("delete from links where src=dst")
    db.commit()
print('== 完成 ==' if not DRY else '== DRY 结束 ==')
