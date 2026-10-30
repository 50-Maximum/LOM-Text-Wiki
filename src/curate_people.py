# -*- coding: utf-8 -*-
"""人物整理：合并同一人、改前缀、改筛选、补绰号。跑在 build_wiki2.py 之后。"""
import sqlite3, json, io, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
DB = os.path.join(BASE, 'data', 'wiki.db')
DRY = '--dry' in sys.argv
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
c = db.cursor()

MERGE = {
    '飞石帮主': '石公远', '沧帮帮主': '江澜', '极乐左使': '李元弃', '极乐教主': '申屠龙',
    '公主': '瑞杏', '姚不知名': '无相祖师', '刘法王': '刘颚', '白虹剑客': '徐光辉',
    '阿叔': '青蛇老怪', '申屠道长': '申屠龙',
}
RENAME = {'唐许亚霆': '唐亚霆', '唐皮康': '唐康', '阿鹤侠': '张姓怪客', '沂国公主': '完颜梦'}
PREFIX = {
    '虞小梅': '飞天门', '丹霞子': '飞天门', '胡离火': '飞天门', '许胜': '飞天门',    '魏菊': '玄功洞', '黄佩华': '玄功洞', '鞠冬音': '玄功洞', '阎罗生': '玄功洞', '呼延菊': '玄功洞',
    '余麟': '夺魄门', '姚知命': '夺魄门',
    '童大虫': '铁拳门', '孟瞋': '铁拳门', '邓夷': '铁拳门',
    '夏侯兰': '雪山派', '金乌上人': '崆峒派', '梁有诗': '江湖', '赵活的娘': '市井',
    '狗鸡': '丐帮', '何兄': '江湖', '刁民': '江湖', '钟老爷': '江湖', '吕姑娘': '市井',
    '张姓怪客': '江湖', '李元弃': '极乐教',
    '李紫穹': '千灯楼',
}
TITLE = {
    '谭霸刀': '破山斩', '曾文': '文盟主', '呼延菊': '前玄功嫡传女弟子', '邓夷': '前铁拳掌门',
    '张姓怪客': '阿鹤侠', '完颜梦': '沂国公主', '段婉清': '宁阳郡主', '徐光辉': '白虹剑客',
    '余自咏': '花城四少', '南宫深': '花城四少', '段智秀': '花城四少',
    '成溪': '花城四少', '金乌上人': '喇嘛',
    '李紫穹': '天驷爽彦贲',
}
FACET = {
    '夏灵犀': '其他', '沧帮帮主': '上官世家', '江澜': '上官世家',
    '梁有诗': '江湖', '赵活的娘': '市井', '狗鸡': '丐帮',
    '何兄': '江湖', '刁民': '江湖', '钟老爷': '江湖', '吕姑娘': '市井',
    '张姓怪客': '江湖', '夏侯兰': '雪山派', '金乌上人': '崆峒派',
    '李元弃': '极乐教', '李紫穹': '千灯楼',
}
SMALL_TO_OTHER = ['苗疆巫灵教', '西夏', '大蒙古国', '天武门', '宇文世家', '梦境']
TOUCH = set(list(MERGE) + list(RENAME) + list(PREFIX) + list(TITLE) + list(FACET))

rows = [dict(r) for r in c.execute("select * from pages where type='人物'")]
by_base = {r['slug'].split('/', 1)[1]: r for r in rows}

def secs_of(r):
    try:
        return json.loads(r['sections'] or '[]')
    except Exception:
        return []

plan = []
print('== 合并 ==')
for src, dst in MERGE.items():
    s, d = by_base.get(src), by_base.get(dst)
    if not s or not d:
        print('  缺页，跳过:', src, '->', dst)
        continue
    print('  %s -> %s' % (s['name'], d['name']))
    plan.append(('merge', src, dst))

print('== 改名 / 前缀 / 绰号 / 筛选 ==')
for r in rows:
    base = r['slug'].split('/', 1)[1]
    if base in MERGE or base not in TOUCH:
        continue
    new_base = RENAME.get(base, base)
    pref = PREFIX.get(new_base) or PREFIX.get(base)
    if not pref:
        pref = (r['name'] or '').split('·')[0] if '·' in (r['name'] or '') else ''
    new_name = ('%s·%s' % (pref, new_base)) if pref else new_base
    title = TITLE.get(new_base, r['title'] or '')
    facet = FACET.get(new_base) or r['facet']
    if new_name != r['name'] or title != (r['title'] or '') or facet != r['facet']:
        print('  %s -> %s | 绰号=%s | 筛选=%s' % (r['name'], new_name, title or '—', facet))
        plan.append(('edit', r['slug'], new_name, title, facet))

# 模拟最终筛选分布
sim = {}
for r in rows:
    base = r['slug'].split('/', 1)[1]
    if base in MERGE:
        continue
    fac = FACET.get(RENAME.get(base, base)) or FACET.get(base) or r['facet']
    pref = PREFIX.get(RENAME.get(base, base)) or PREFIX.get(base)
    if pref in ('飞天门', '玄功洞', '夺魄门', '铁拳门'):
        fac = '崆峒派'
    if fac == '玄功门':
        fac = '崆峒派'
    sim[r['slug']] = fac
cnt = collections.Counter(sim.values())
print('== 崆峒四门与沧帮的筛选并合 ==')
for f in ('飞天门', '夺魄门', '铁拳门', '玄功门'):
    if cnt.get(f):
        print('  %s（%d 人）-> 崆峒派' % (f, cnt[f]))
if cnt.get('沧帮'):
    print('  沧帮（%d 人）-> 上官世家' % cnt['沧帮'])
print('== 人少的并到「其他」 ==')
for f in SMALL_TO_OTHER:
    if cnt.get(f):
        print('  %s（%d 人）-> 其他' % (f, cnt[f]))

if DRY:
    print('== DRY 结束，未写入 ==')
    sys.exit(0)

for act in plan:
    if act[0] == 'merge':
        src, dst = act[1], act[2]
        s, d = by_base[src], by_base[dst]
        ds = secs_of(d)
        idx = {x.get('h'): x for x in ds}
        for sec in secs_of(s):
            if sec.get('h') == '脚注':
                continue
            t = idx.get(sec.get('h'))
            if t is None:
                ds.append(sec)
                idx[sec.get('h')] = sec
            else:
                have = {(x.get('note'), x.get('script')) for x in (t.get('rows') or [])}
                for x in (sec.get('rows') or []):
                    if (x.get('note'), x.get('script')) not in have:
                        t.setdefault('rows', []).append(x)
        c.execute("update pages set sections=? where slug=?",
                  (json.dumps(ds, ensure_ascii=False), d['slug']))
        for al in (src, s['name']):
            c.execute("insert or replace into aliases values(?,?)", (al, d['slug']))
        c.execute("update links set dst=? where dst=?", (d['slug'], s['slug']))
        c.execute("update links set src=? where src=?", (d['slug'], s['slug']))
        c.execute("delete from pages where slug=?", (s['slug'],))
    else:
        _, slug, name, title, facet = act
        c.execute("update pages set name=?, title=?, facet=? where slug=?", (name, title, facet, slug))
        c.execute("insert or replace into aliases values(?,?)", (slug.split('/', 1)[1], slug))

for f in ('飞天门', '夺魄门', '铁拳门', '玄功门'):
    c.execute("update pages set facet='崆峒派' where type='人物' and facet=?", (f,))
c.execute("update pages set facet='上官世家' where type='人物' and facet='沧帮'")
for f in SMALL_TO_OTHER:
    c.execute("update pages set facet='其他' where type='人物' and facet=?", (f,))

c.execute("delete from links where src=dst")
db.commit()
print('== 已写入 ==')
