# -*- coding: utf-8 -*-
"""人物归属微调：把 data/member_override.json 里的人从原势力成员表挪到目标势力。
幂等，跑在 curate_people.py 之后（build 会按旧名前缀生成成员表，curate 改名后需再挪一次）。"""
import sqlite3, json, os, sys, io
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
OVR = os.path.join(BASE, 'data', 'member_override.json')
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()

if not os.path.exists(OVR):
    print('无 member_override.json，跳过')
    sys.exit(0)
ovr = json.load(open(OVR, encoding='utf-8'))

title_of = {}
for r in c.execute("select slug,name,title from pages where type='人物'"):
    base = r['name'].split('·', 1)[-1]
    title_of[base] = r['title'] or ''

moved = 0
for base, target in ovr.items():
    tslug = '势力/' + target
    if not c.execute("select 1 from pages where slug=?", (tslug,)).fetchone():
        print('  缺势力页', target, '跳过', base)
        continue
    t = title_of.get(base) or ''

    # 1) 从所有其他势力成员表里摘掉
    for r in list(c.execute("select slug,sections,infobox from pages where type='势力'")):
        if r['slug'] == tslug:
            continue
        try:
            secs = json.loads(r['sections'] or '[]')
        except Exception:
            continue
        hit = False
        for s in secs:
            if not (s.get('h') or '').startswith('本派成员'):
                continue
            rows = s.get('rows') or []
            keep = [x for x in rows if (x.get('title') or '') != base]
            if len(keep) != len(rows):
                hit = True
                s['rows'] = keep
                s['h'] = '本派成员（%d 人）' % len(keep)
        if hit:
            inf = json.loads(r['infobox'] or '{}')
            inf['成员'] = '%d 人' % max(0, int(str(inf.get('成员', '0 人')).rstrip(' 人') or 0) - 1)
            c.execute("update pages set sections=?, infobox=? where slug=?",
                      (json.dumps(secs, ensure_ascii=False), json.dumps(inf, ensure_ascii=False), r['slug']))
            old = r['slug']
            c.execute("delete from links where src=? and dst=? and kind='成员'", (old, '人物/' + base))
            c.execute("delete from links where src=? and dst=? and kind='归属'", ('人物/' + base, old))
            moved += 1

    # 2) 放进目标势力成员表
    r = c.execute("select sections,infobox from pages where slug=?", (tslug,)).fetchone()
    secs = json.loads(r['sections'] or '[]')
    idx = None
    for i, s in enumerate(secs):
        if (s.get('h') or '').startswith('本派成员'):
            idx = i
            break
    row = {"note": (base + '｜「' + t + '」') if t else base,
           "quote": "", "script": "", "title": base, "seq": 0, "routes": []}
    if idx is None:
        secs.append({"h": "本派成员（1 人）", "rows": [row]})
        added = True
    else:
        rows = secs[idx].get('rows') or []
        added = not any((x.get('title') or '') == base for x in rows)
        if added:
            rows.append(row)
            secs[idx]['rows'] = rows
            secs[idx]['h'] = '本派成员（%d 人）' % len(rows)
    inf = json.loads(r['infobox'] or '{}')
    cnt = len([x for s in secs if (s.get('h') or '').startswith('本派成员') for x in (s.get('rows') or [])])
    inf['成员'] = '%d 人' % cnt
    c.execute("update pages set sections=?, infobox=? where slug=?",
              (json.dumps(secs, ensure_ascii=False), json.dumps(inf, ensure_ascii=False), tslug))

    if c.execute("select 1 from pages where slug=?", ('人物/' + base,)).fetchone():
        if not c.execute("select 1 from links where src=? and dst=? and kind='归属'",
                         ('人物/' + base, tslug)).fetchone():
            c.execute("insert into links(src,dst,kind,label) values(?,?,?,?)",
                      ('人物/' + base, tslug, '归属', ''))
        if not c.execute("select 1 from links where src=? and dst=? and kind='成员'",
                         (tslug, '人物/' + base)).fetchone():
            c.execute("insert into links(src,dst,kind,label) values(?,?,?,?)",
                      (tslug, '人物/' + base, '成员', ''))
    print('  %s -> %s  %s' % (base, target, '新增' if added else '已在'))

db.commit()
print('归属微调完成，移动 %d 处' % moved)
