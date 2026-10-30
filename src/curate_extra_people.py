# -*- coding: utf-8 -*-
"""补充人物与别名：只靠台词出现、不在立绘表里的条目，以及称号合并。
目前含：成溪（花城四少）、温无暇（碧箫仙子）、朝阳剑客→盛鸿年 的合并。
幂等：重复运行只更新不重复插入。"""
import sqlite3, os, io, sys, json
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()
log = []

PEOPLE = [
    dict(slug='人物/成溪', name='扬州·成溪', title='花城四少', faction='江湖',
         lead='扬州人，自称「花城四少」。武林大会群侠叫阵时，他报出名号向赵活挑战，此后再无登场。',
         note='1. 自称扬州「花城四少」，在武林大会上向赵活叫阵，此后再无登场。',
         quote='扬州『花城四少』成溪，领教高招！', script='ch6_6_1', seq=215,
         scene_title='向无忧连战群雄', stage='第6章·武林大会'),
    dict(slug='人物/温无暇', name='峨嵋派·温无暇', title='碧箫仙子', faction='峨嵋派',
         lead='峨嵋派温无畏的妹妹，人称「碧箫仙子」。只在南宫远追述旧事时被提到一次，未在剧情中登场。',
         note='1. 南宫远追述七变圣手温无畏时，提到其妹碧箫仙子温无暇。',
         quote='可还记得当年七变圣手温无畏，与他妹妹碧箫仙子温无暇', script='ch6_7_1', seq=242,
         scene_title='南宫远就任武林盟主', stage='第6章·武林大会'),
]

for p in PEOPLE:
    info = {'势力': p['faction'], '出现阶段': p['stage']}
    secs = [{'h': '备注', 'rows': [{'note': p['note'], 'quote': p['quote'],
                                    'script': p['script'], 'title': p['scene_title'],
                                    'seq': p['seq'], 'routes': []}]}]
    cats = ['人物', p['faction'], '第6章', p['stage']]
    row = c.execute("select slug from pages where slug=?", (p['slug'],)).fetchone()
    if row:
        c.execute("update pages set name=?,title=?,lead=?,infobox=?,sections=?,cats=?,facet=? where slug=?",
                  (p['name'], p['title'], p['lead'], json.dumps(info, ensure_ascii=False),
                   json.dumps(secs, ensure_ascii=False), json.dumps(cats, ensure_ascii=False),
                   p['faction'], p['slug']))
        log.append('更新 ' + p['slug'])
    else:
        c.execute("""insert into pages(slug,type,name,lead,infobox,sections,cats,mentions,chapters,
                     sort_key,title,hidden,facet,facet2) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (p['slug'], '人物', p['name'], p['lead'], json.dumps(info, ensure_ascii=False),
                   json.dumps(secs, ensure_ascii=False), json.dumps(cats, ensure_ascii=False),
                   1, json.dumps(['第6章', p['stage']], ensure_ascii=False),
                   '', p['title'], 0, p['faction'], ''))
        log.append('新建 ' + p['slug'])
    if not c.execute("select 1 from aliases where alias=?", (p['name'].split('·')[-1],)).fetchone():
        c.execute("insert into aliases(alias,slug) values(?,?)", (p['name'].split('·')[-1], p['slug']))
    for a, b, k, lb in ((p['slug'], '场景/' + p['script'], '提及场景', ''),
                        ('场景/' + p['script'], p['slug'], '提及场景', '')):
        if not c.execute("select 1 from links where src=? and dst=?", (a, b)).fetchone():
            c.execute("insert into links(src,dst,kind,label) values(?,?,?,?)", (a, b, k, lb))

# 朝阳剑客 → 盛鸿年
OLD, NEW = '人物/朝阳剑客', '人物/盛鸿年'
if c.execute("select 1 from pages where slug=?", (OLD,)).fetchone():
    c.execute("update links set src=? where src=?", (NEW, OLD))
    c.execute("update links set dst=? where dst=?", (NEW, OLD))
    c.execute("delete from pages where slug=?", (OLD,))
    log.append('删除旧条目 ' + OLD)
c.execute("update aliases set slug=? where alias='朝阳剑客'", (NEW,))
if not c.execute("select 1 from aliases where alias='朝阳剑客'").fetchone():
    c.execute("insert into aliases(alias,slug) values('朝阳剑客',?)", (NEW,))
if c.execute("select 1 from redirects where alias='朝阳剑客'").fetchone():
    c.execute("update redirects set slug=? where alias='朝阳剑客'", (NEW,))
else:
    c.execute("insert into redirects(alias,slug) values('朝阳剑客',?)", (NEW,))
# 温无暇与温无畏的兄妹关系
for a, b in (('人物/温无暇', '人物/温无畏'), ('人物/温无畏', '人物/温无暇')):
    if not c.execute("select 1 from links where src=? and dst=? and kind='关系'", (a, b)).fetchone():
        c.execute("insert into links(src,dst,kind,label) values(?,?,?,?)", (a, b, '关系', '兄妹'))
db.commit()
print('完成：%d 项改动' % len(log))
for x in log:
    print('  ' + x)
