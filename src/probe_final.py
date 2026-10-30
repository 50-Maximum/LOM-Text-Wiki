# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json, sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
b = 'http://127.0.0.1:8765'
t = json.load(urllib.request.urlopen(b + '/api/types'))
print({x['type']: x['n'] for x in t['types'] if x['type'] in ('世界观','地点','势力','人物','武学','战技')})
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
n_lead = c.execute("select count(*) from pages where lead!=''").fetchone()[0]
n_fn = 0
for (secs,) in c.execute('select sections from pages'):
    try:
        if any(s.get('h') == '脚注' for s in json.loads(secs)):
            n_fn += 1
    except Exception:
        pass
print('有导语页数', n_lead, '含脚注页数', n_fn)
