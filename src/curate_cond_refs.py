# -*- coding: utf-8 -*-
"""给页面里出现的条件编号就地补上条件原文（单次扫描，不会嵌套）。

  判定 Ch_1_1_1_001 结果 1        → 判定 Ch_1_1_1_001（掌门找你的原因？） 结果 1
  Ch_0_6_004（按结果走不同剧情）   → Ch_0_6_004（条件：……；按结果走不同剧情）

幂等：编号后已经跟「（」的一律不动。条件页自身不改。
"""
import sqlite3, json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()

LIB = json.load(open(os.path.join(BASE, 'data', 'cond_lib.json'), encoding='utf-8'))
try:
    for _id, _at in c.execute("select id, attrs from cond"):
        _key = _id[:-5] if _id.endswith('@cond') else _id
        if _key in LIB:
            continue
        try:
            _a = json.loads(_at or '[]')
        except Exception:
            _a = []
        if _a:
            LIB[_key] = {'attrs': _a}
except Exception:
    pass

CAP = 34


def short(cid):
    a = (LIB.get(cid) or {}).get('attrs') or []
    if not a:
        return ''
    t = re.sub(r'\s+', ' ', a[0]).strip()
    return t if len(t) <= CAP else t[:CAP] + '…'


IDS = sorted([k for k in LIB if re.match(r'^[A-Za-z][A-Za-z0-9_]+$', k)], key=len, reverse=True)
PAT = re.compile(r'(?<![A-Za-z0-9_])(' + '|'.join(re.escape(k) for k in IDS) + r')(?![A-Za-z0-9_])')


def fix(text):
    if not text or not re.search(r'[A-Za-z]', text):
        return text, 0
    n = 0

    def _one(m):
        nonlocal n
        cid = m.group(1)
        s = short(cid)
        if not s:
            return m.group(0)
        # 原文已经在这段里出现过了，就不再插第二遍
        if s in text:
            return m.group(0)
        tail = text[m.end():m.end() + 16]
        if tail.startswith('（按结果走不同剧情'):
            n += 1
            return cid + '（条件：' + s + '；'
        # 后面跟冒号/括号/逗号，说明原文或结构已经有了
        if tail[:1] in ('（', '：', '）', '，', ';', '；'):
            return m.group(0)
        n += 1
        return cid + '（' + s + '）'

    text = PAT.sub(_one, text)
    return text, n


tot_pages = tot_hits = 0
for r in list(c.execute("select slug,type,lead,sections from pages where type<>'条件'")):
    lead = r['lead'] or ''
    try:
        secs = json.loads(r['sections'] or '[]')
    except Exception:
        continue
    n = 0
    nl, k1 = fix(lead)
    if k1:
        lead, n = nl, n + k1
    for s in secs:
        for row in (s.get('rows') or []):
            for key in ('note', 'quote', 'label', 'title'):
                v = row.get(key)
                if isinstance(v, str):
                    nv, k = fix(v)
                    if k:
                        row[key] = nv
                        n += k
        if isinstance(s.get('html'), str):
            nv, k = fix(s['html'])
            if k:
                s['html'] = nv
                n += k
    if n:
        c.execute("update pages set lead=?, sections=? where slug=?",
                  (lead, json.dumps(secs, ensure_ascii=False), r['slug']))
        tot_pages += 1
        tot_hits += n

db.commit()
print('条件编号补原文：%d 页，%d 处' % (tot_pages, tot_hits))
