# -*- coding: utf-8 -*-
"""把重写的剧情段概要写回页面：落在导语，并同步到「本段事件」段的首段文字。"""
import sqlite3, os, io, sys, json
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
SUM = json.load(io.open(os.path.join(BASE, 'data', 'seg_sum.json'), encoding='utf-8'))
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()

n = 0
miss = []
for slug, d in SUM.items():
    txt = (d.get('lead') or '').strip()
    if not txt:
        continue
    r = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        miss.append(slug)
        continue
    secs = json.loads(r['sections'] or '[]')
    for s in secs:
        if (s.get('h') or '') == '本段事件':
            s['html'] = txt
    c.execute("update pages set lead=?, sections=? where slug=?",
              (txt, json.dumps(secs, ensure_ascii=False), slug))
    n += 1
db.commit()
print('写入 %d 页；缺页 %d %s' % (n, len(miss), miss[:5]))
