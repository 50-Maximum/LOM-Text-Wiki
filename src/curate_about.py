# -*- coding: utf-8 -*-
"""按库内实际页面数刷新「关于」页的收录规模。
跑在全部 curate 之后，避免 build 时算的数字与最终库不一致。"""
import sqlite3, os, io, sys, json
sys.stdout.reconfigure(encoding='utf-8')
DB = os.path.join(os.getcwd(), 'data', 'wiki.db')
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()

counts = {t: n for t, n in c.execute("select type,count(*) from pages group by type")}
# 关于页里一行一个类型；数值类（属性/旗标/设施）合并显示
ALIAS = {'数值': ('数值',)}
rows = c.execute("select slug,lead,sections from pages where type='关于'").fetchone()
if not rows:
    print('没有关于页')
    sys.exit(0)
secs = json.loads(rows['sections'] or '[]')
changed = 0
for s in secs:
    if (s.get('h') or '') != '收录规模':
        continue
    new = []
    for x in (s.get('rows') or []):
        note = x.get('note') or ''
        label = note.split('：')[0].strip()
        if label in counts:
            t = '数值' if label == '数值' else label
            n = counts.get(t, counts.get(label, 0))
            if label == '数值':
                n = counts.get('数值', 0)
            nn = '%s：%d 条' % (label, n)
            if nn != note:
                changed += 1
            x['note'] = nn
        new.append(x)
    s['rows'] = new
c.execute("update pages set sections=? where type='关于'",
          (json.dumps(secs, ensure_ascii=False),))

# 已知局限里补一条旗标推断覆盖率（数字跟着库变，不写死）
try:
    INFER = json.load(io.open(os.path.join(os.getcwd(), 'data', 'flag_infer.json'), encoding='utf-8'))
except Exception:
    INFER = {}
nflag = c.execute("select count(*) from pages where slug glob '数值/旗标_*'").fetchone()[0]
nnick = c.execute("select count(*) from pages where slug glob '数值/旗标_*' and name like '%暂称%'").fetchone()[0]
nhand = sum(1 for k, v in INFER.items() if not (v.get('note') or '').startswith('（按写入现场自动归纳') and not (v.get('note') or '').startswith('（读剧本归纳'))
nread = sum(1 for k, v in INFER.items() if (v.get('note') or '').startswith('（读剧本归纳'))
nmiss = sum(1 for k, v in INFER.items()
            if any(w in (v.get('note') or '') for w in ('没有写入点', '查无写入点', '未见写入点')))
npage = c.execute("select count(*) from pages where slug glob '数值/旗标_*' and lead is not null and lead != ''").fetchone()[0]
line = ('五、旗标 %d 个，含义就写在每页开头那一句里：%d 条早期人工整理，%d 条按写入现场的台词逐条归纳，'
        '其中有 %d 条在 2,147 个剧本里找不到写入点（由游戏系统写），已如实注明。'
        '没有官方名的用「暂称」，名取自它所在的那场戏（共 %d 个），页内已注明是本站拟名、不是游戏原文。'
        'A00001、Z00001 这类名字里的「旗标暂存N」是官方表给的通用占位名，也不是专名。'
        % (nflag, nhand, nread, nmiss, nnick))
for s in secs:
    if (s.get('h') or '') != '已知局限':
        continue
    html = s.get('html') or ''
    html = '\n'.join(x for x in html.split('\n') if not x.startswith('五、'))
    s['html'] = (html + '\n' + line).strip()
c.execute("update pages set sections=? where type='关于'",
          (json.dumps(secs, ensure_ascii=False),))
db.commit()
print('刷新关于页计数 %d 行' % changed)
