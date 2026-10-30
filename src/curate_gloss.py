# -*- coding: utf-8 -*-
"""给 pages 里所有裸旗标编号补〔人话〕。用回调判断，避免正则回溯截断编号。
默认预演，加 --write 才落库。"""
import sqlite3, os, io, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
D = lambda n: json.load(io.open(os.path.join(BASE, 'data', n), encoding='utf-8'))
gloss = D('flag_gloss.json')
fname = D('flag_names.json')
NPAT = re.compile(r'旗标\s*([A-Za-z][A-Za-z0-9_]+)')


def label(f):
    nm = fname.get(f) or ''
    if isinstance(nm, dict):
        nm = nm.get('name') or ''
    if nm and not re.search(r'旗标暂存', nm):
        return nm
    g = gloss.get(f)
    if isinstance(g, dict):
        g = g.get('text')
    return g or ''


def add_gloss(text):
    if not text or '旗标' not in text:
        return text, 0
    out, last, n = [], 0, 0
    for m in NPAT.finditer(text):
        f = m.group(1)
        after = text[m.end():]
        if after.startswith('〔') or after.startswith('[') or after.startswith('（'):
            continue
        lab = label(f)
        if not lab:
            continue
        out.append(text[last:m.end()])
        out.append('〔%s〕' % lab)
        last = m.end()
        n += 1
    if not n:
        return text, 0
    out.append(text[last:])
    return ''.join(out), n


db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()
changed_pages = changed_rows = total = 0
miss = {}
for r in c.execute("select slug,sections from pages").fetchall():
    secs = json.loads(r['sections'] or '[]')
    touched = 0
    for s in secs:
        for row in (s.get('rows') or []):
            note = row.get('note') or ''
            if '旗标' not in note:
                continue
            for m in NPAT.finditer(note):
                total += 1
                if not label(m.group(1)):
                    miss[m.group(1)] = miss.get(m.group(1), 0) + 1
            new, n = add_gloss(note)
            if n:
                row['note'] = new
                touched += n
    if touched:
        c.execute("update pages set sections=? where slug=?",
                  (json.dumps(secs, ensure_ascii=False), r['slug']))
        changed_pages += 1
        changed_rows += touched
db.commit()

o = io.open('_gloss_apply.txt', 'w', encoding='utf-8')
o.write('%s：改动页面 %d，补注 %d 处；原文裸编号共 %d 处\n'
        % ('已写入', changed_pages, changed_rows, total))
o.write('仍无解释 %d 种、%d 次\n' % (len(miss), sum(miss.values())))
for f, n in sorted(miss.items(), key=lambda x: -x[1])[:12]:
    o.write('  %-14s x%d\n' % (f, n))
o.close()
print('ok')
