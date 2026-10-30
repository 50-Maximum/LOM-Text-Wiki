# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json, sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
b = 'http://127.0.0.1:8765'

# 1) 搜索是否返回原文行
q = urllib.parse.quote('唐布衣')
d = json.load(urllib.request.urlopen(b + '/api/search2?q=' + q))
print('搜索 唐布衣 -> 条目', len(d.get('pages', [])), '场景', len(d.get('scenes', [])), '原文', len(d.get('lines', [])))
if d.get('lines'):
    print('  首条:', d['lines'][0])

# 2) 脚注是否带 seq
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for slug in ("人物/申屠龙", "人物/魏菊", "人物/叶云裳"):
    r = c.execute("select lead,sections from pages where slug=?", (slug,)).fetchone()
    secs = json.loads(r[1])
    fn = [s for s in secs if s['h'] == '脚注']
    seqs = [row.get('seq') for s in fn for row in s['rows']]
    print(slug, '脚注 seq:', seqs)
    print('   lead 含柳家?', '柳家' in r[0])
    br = [s for s in secs if s['h'] in ('分支', '收徒与分支')]
    if br:
        print('   分支:', br[0]['html'][:80])
