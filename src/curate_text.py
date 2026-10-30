# -*- coding: utf-8 -*-
"""文案收尾：修简介、补出场场景、合并重复章节。跑在 build 与另两个 curate 之后。"""
import sqlite3, json, io, os, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')
db = sqlite3.connect(os.path.join(os.getcwd(), 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()
DRY = '--dry' in sys.argv

LEADS = {
    '江湖·方震天': None,
    '方震天': '方震天，无门无派的游侠，惯用刀，以挑战成名高手为务。他登门向唐布衣发起挑战，'
              '讥讽赵活只是开胃小菜（1）；被龙湘拦下后，卖面子离开（2）。败给赵活后，'
              '他扬言下次要赵活付出血的代价（3）。在武林大会上，他由静江府九地山水盟推举，'
              '向上官隼讨教金背龙王刀法（4）。后来他再次登门挑战唐布衣，被拒后扬言要杀唐家掌门（5）；'
              '若败给赵活，他仍不服，自认只是常有的挫折，扬言下次会更强。',
    '裴红腊': '裴红腊是青城派弟子，由不平长老推派参加十代长老的演武试艺。他至今不肯受道号，'
              '仍以俗名行走门派；平日在被窝里读书写字，床底私藏陆大诗人的词集，'
              '被不平长老搜出后当面争执，直言自己本来就不想习武。',
    '路人侠': '路人侠是游戏对无名江湖人的统称，并不指同一个人：原文以 ranger1、ranger2、ranger3、'
              'ranger5 四个不同立绘分别指代不同的路人。茶肆里议论叶家兄妹的是 ranger1 与 ranger2，'
              '两人一唱一和、彼此并不相识；上门寻衅、追到唐门的又是另一位。此处按统称汇总，'
              '具体是哪一位，以各场景页标出的立绘角色为准。',
}

def secs_of(r):
    try:
        return json.loads(r['sections'] or '[]')
    except Exception:
        return []

print('== 修简介 ==')
for key, lead in LEADS.items():
    if not lead:
        continue
    r = c.execute("select slug,lead from pages where type='人物' and name like ?", ('%' + key,)).fetchone()
    if not r:
        print('  缺页', key)
        continue
    if (r['lead'] or '') == lead:
        continue
    print('  %s 已更新' % r['slug'])
    if not DRY:
        c.execute("update pages set lead=? where slug=?", (lead, r['slug']))

print('== 补出场场景（赵扩） ==')
r = c.execute("select slug,sections from pages where type='人物' and name like '%赵扩'").fetchone()
if r:
    secs = secs_of(r)
    if not any((s.get('h') or '') == '出场场景' for s in secs):
        rows = []
        for x in c.execute("select script,title from scenes where script in "
                           "(select distinct script from lines where speaker like '%赵扩%' "
                           "or text like '%赵扩%' or speaker like '%皇帝%') limit 12"):
            rows.append({'note': x['title'] or x['script'], 'quote': '', 'script': x['script'],
                         'title': x['title'] or x['script'], 'seq': 0, 'routes': []})
        if rows:
            secs.append({'h': '出场场景', 'rows': rows})
            print('  赵扩补 %d 场' % len(rows))
            if not DRY:
                c.execute("update pages set sections=? where slug=?",
                          (json.dumps(secs, ensure_ascii=False), r['slug']))

print('== 同名群像说明 ==')
GROUP = ['唐门弟子', '唐门女弟子', '青城弟子', '夺魄弟子', '铁拳弟子', '飞天弟子', '玄功弟子',
         '点苍弟子', '峧嵋弟子', '崧山弟子', '全真弟子', '锦香弟子', '岭南弟子', '沧帮弟子',
         '路人侠', '路人', '乞丐', '山贼', '歹人', '妇人', '少女', '少年', '大妈', '鬼卒',
         '铜人', '蒙面人', '店小二', '南宫家丁', '飞石帮']
N2I = {}
for _ln in io.open(os.path.join(os.getcwd(), 'data', 'raw', 'system', 'Character_zh-cn.txt'),
                   encoding='utf-8', errors='replace'):
    _m = re.match(r'Character/(\S+)\s*=\s*(.+?)\s*$', _ln)
    if _m:
        N2I.setdefault(_m.group(2), []).append(_m.group(1))
for base in GROUP:
    ids = sorted(set(N2I.get(base) or []))
    if len(ids) < 2:
        continue
    r = c.execute("select slug,sections from pages where type='人物' and slug=?", ('人物/' + base,)).fetchone()
    if not r:
        continue
    secs = secs_of(r)
    secs = [s for s in secs if (s.get('h') or '') != '同名说明']
    note = ('此名号在原文中由 %d 个不同立绘共用（%s），指代的是不同的无名角色，并非同一人。'
            '页面里凡标此名号的台词，只能读作「其中某一个%s」所说。' % (len(ids), '、'.join(ids), base))
    secs.insert(0, {'h': '同名说明', 'html': note})
    if not DRY:
        c.execute("update pages set sections=? where slug=?",
                  (json.dumps(secs, ensure_ascii=False), r['slug']))
    print('  %s：%d 个立绘' % (base, len(ids)))

print('== 青城长老消歧页 ==')
_rows = [{'note': '%s（%s）' % (n, d), 'quote': '', 'script': '', 'title': n, 'seq': 0, 'routes': []}
         for n, d in (('怀素真人', 'daoshi311'), ('不平道长', 'daoshi312'), ('铁冠道人', 'daoshi313'))]
_lead = ('「青城长老」是剧本里的共用称呼，实际由三个不同的人分别充当：怀素、不平、铁冠。'
         '原文显示名都是「青城长老」，只有立绘资源不同；本页只做指认，具体台词已按立绘拆到各自条目。')
_secs_q = [{'h': '同名说明', 'html': _lead}, {'h': '指认为', 'rows': _rows}]
if not DRY:
    c.execute("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              ('人物/青城长老', '人物', '青城派·青城长老（共用称呼）', _lead,
               json.dumps({'类型': '人物', '所属': '青城派'}, ensure_ascii=False),
               json.dumps(_secs_q, ensure_ascii=False),
               json.dumps(['人物', '青城派'], ensure_ascii=False), 0, '[]', '', '', 0, '青城派', ''))
print('  已写入消歧页')

print('== 合并重复章节 ==')
allrows = list(c.execute("select slug,sections from pages"))
n = 0
for r in allrows:
    secs = secs_of(r)
    hs = [(s.get('h') or '') for s in secs]
    dup = {h for h, k in collections.Counter(hs).items() if k > 1 and h}
    if not dup:
        continue
    out, idx = [], {}
    for s in secs:
        h = s.get('h') or ''
        if h in dup:
            if h in idx:
                t = idx[h]
                have = {(x.get('note'), x.get('script')) for x in (t.get('rows') or [])}
                for x in (s.get('rows') or []):
                    if (x.get('note'), x.get('script')) not in have:
                        t.setdefault('rows', []).append(x)
                if s.get('html') and s['html'] not in (t.get('html') or ''):
                    t['html'] = ((t.get('html') or '') + '\n' + s['html']).strip()
                continue
            idx[h] = s
        out.append(s)
    n += 1
    if not DRY:
        c.execute("update pages set sections=? where slug=?",
                  (json.dumps(out, ensure_ascii=False), r['slug']))
print('  合并 %d 页' % n)

if not DRY:
    db.commit()
print('== 完成 ==' if not DRY else '== DRY ==')
