# -*- coding: utf-8 -*-
"""地点页「发生场景」栏对齐：按 data/scenes_by_place.json 补齐并改写计数。
修的问题是部分地点页（如破庙）infobox 有「N 场」却列不出场景。跑在 build 之后。"""
import sqlite3, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
MAP = os.path.join(BASE, 'data', 'scenes_by_place.json')
if not os.path.exists(MAP):
    print('无 scenes_by_place.json，跳过')
    sys.exit(0)

SBP = json.load(open(MAP, encoding='utf-8'))
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()
titles = {r['script']: r['title'] for r in c.execute("select script,title from scenes")}

fixed = 0
for r in list(c.execute("select slug,name,sections,infobox from pages where type='地点'")):
    scs = SBP.get(r['name']) or []
    if not scs:
        continue
    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        continue
    try:
        inf = json.loads(r['infobox'] or '{}')
    except Exception:
        inf = {}
    rows = [{"note": titles.get(x) or x, "quote": "", "script": x,
             "title": titles.get(x) or x, "seq": 0, "routes": []} for x in scs[:60]]
    idx = None
    for i, s in enumerate(secs):
        if (s.get('h') or '').startswith('发生场景'):
            idx = i
            break
    if idx is None:
        secs.append({"h": "发生场景", "rows": rows})
    else:
        secs[idx] = {"h": "发生场景", "rows": rows}
    inf['场景'] = '%d 场' % len(scs)
    c.execute("update pages set sections=?, infobox=? where slug=?",
              (json.dumps(secs, ensure_ascii=False), json.dumps(inf, ensure_ascii=False), r['slug']))
    fixed += 1
db.commit()
print('地点场景栏处理 %d 页' % fixed)
