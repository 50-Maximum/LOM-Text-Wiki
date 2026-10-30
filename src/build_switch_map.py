# -*- coding: utf-8 -*-
"""建「剧本内分歧变量」对照表。

产出 data/switch_map.json：
  { script: { "switch1_1_result": {"id": "M40040_01", "line": 60},
              "switch_008_result": {"id": "M40065_01", "line": 688} }, ... }
产出 data/checkpoint_res.json：
  { "M40065_01": [ {"script": "ch5_1_1", "res": 1, "line": 689, "text": "……"}, ... ] }
产出 data/flag_write_ctx.json：
  { "M40065": [ {"script": "ch4_6_12", "line": 29, "op": "SetFlag", "value": "1", "text": "……"} ] }
"""
import io, os, re, sys, json, glob, sqlite3
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
SCR = os.path.join(BASE, 'data', 'raw', 'scripts')
o = io.open('_sm_build.txt', 'w', encoding='utf-8')

# D_xxx → 台词
TEXT = {}
for fn in glob.glob(os.path.join(BASE, 'data', 'raw', 'story', '*.txt')):
    for ln in io.open(fn, encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*Story/([A-Z]?_[A-Za-z0-9_]+)\s*=\s*(.*)$', ln)
        if m:
            TEXT[m.group(1)] = m.group(2).replace('\\n', ' ').strip()

SW = re.compile(r'local\s+(switch[A-Za-z0-9_]*_result)\s*=\s*checkpointmanager\.Switch\("([A-Za-z0-9_]+)"\)')
IFS = re.compile(r'(?:^|\s)(?:if|elseif)\s+(switch[A-Za-z0-9_]*_result)\s*==\s*(\d+)\s+then')
TXT = re.compile(r'GetStoryText\("([A-Z]?_[A-Za-z0-9_]+)"\)')
WRITE = re.compile(r'statmodifymanager\.(SetFlag|AddFlag)\("([A-Za-z0-9_]+)",\s*([^)]+)\)')

switch_map = {}
res_map = {}
write_ctx = {}

for fn in sorted(glob.glob(os.path.join(SCR, '*.txt'))):
    sc = os.path.basename(fn)[:-4]
    lines = io.open(fn, encoding='utf-8', errors='ignore').read().splitlines()
    smap = {}
    for i, ln in enumerate(lines):
        m = SW.search(ln)
        if m:
            smap[m.group(1)] = {'id': m.group(2), 'line': i + 1}
    if smap:
        switch_map[sc] = smap
    # 分支结果 → 紧随其后的第一句台词
    for i, ln in enumerate(lines):
        m = IFS.search(ln)
        if not m:
            continue
        var, res = m.group(1), int(m.group(2))
        cid = (smap.get(var) or {}).get('id') or ''
        quote = ''
        for j in range(i + 1, min(len(lines), i + 16)):
            t = TXT.search(lines[j])
            if t:
                quote = TEXT.get(t.group(1), '')
                if quote:
                    break
        if cid:
            res_map.setdefault(cid, []).append(
                {'script': sc, 'res': res, 'line': i + 1, 'text': quote[:90]})
    # 旗标写入点 → 附近台词
    for i, ln in enumerate(lines):
        for m in WRITE.finditer(ln):
            op, flag, val = m.group(1), m.group(2), m.group(3).strip()
            quote = ''
            for j in range(i, min(len(lines), i + 12)):
                t = TXT.search(lines[j])
                if t:
                    q = TEXT.get(t.group(1), '')
                    if q:
                        quote = q
                        break
            if not quote:
                for j in range(max(0, i - 12), i):
                    t = TXT.search(lines[j])
                    if t:
                        q = TEXT.get(t.group(1), '')
                        if q:
                            quote = q
            write_ctx.setdefault(flag, []).append(
                {'script': sc, 'line': i + 1, 'op': op, 'value': val, 'text': quote[:90]})

json.dump(switch_map, io.open(os.path.join(BASE, 'data', 'switch_map.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(res_map, io.open(os.path.join(BASE, 'data', 'checkpoint_res.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(write_ctx, io.open(os.path.join(BASE, 'data', 'flag_write_ctx.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

o.write('剧本 %d 个；含分支变量的 %d 个；判定结果 %d 种；旗标写入点 %d 种\n'
        % (len(glob.glob(os.path.join(SCR, '*.txt'))), len(switch_map), len(res_map), len(write_ctx)))
o.write('\nch5_1_1 变量表（前 6）：\n')
for k, v in list((switch_map.get('ch5_1_1') or {}).items())[:6]:
    o.write('  %s -> %s (行 %d)\n' % (k, v['id'], v['line']))
o.write('\nM40065_01 各结果：\n')
for x in (res_map.get('M40065_01') or [])[:6]:
    o.write('  %s 结果 %d → %s\n' % (x['script'], x['res'], x['text']))
o.write('\nM40065 写入点：%s\n' % json.dumps(write_ctx.get('M40065'), ensure_ascii=False))
o.write('\nM40001 写入点：%s\n' % json.dumps(write_ctx.get('M40001'), ensure_ascii=False)[:400])
o.close()
print('ok')
