# -*- coding: utf-8 -*-
"""剧情单元（block）归属生成：scene → 单元，并给出单元内顺序。

用法：python src/build_blocks.py
输出：data/blocks_map.json
"""
import json, os, re, sqlite3, fnmatch, sys, collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'data', 'wiki.db')
CFG = os.path.join(BASE, 'data', 'stage_blocks.json')
OUTP = os.path.join(BASE, 'data', 'blocks_map.json')


def natkey(s):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]


def main():
    cfg = json.load(open(CFG, encoding='utf-8'))
    blocks = list(cfg['blocks'])
    # 人工读完写的内容单元（data/unit_plan.json）
    try:
        _upp = os.path.join(BASE, 'data', 'unit_plan.json')
        if os.path.exists(_upp):
            for _u in (json.load(open(_upp, encoding='utf-8')).get('units') or []):
                blocks.append({'name': _u['name'], 'arc': _u.get('arc') or '',
                               'place': _u.get('place') or '',
                               'order': _u.get('order') or 1000,
                               'patterns': _u.get('patterns') or []})
    except Exception as _e:
        print('内容单元跳过:', _e)
    fallback = cfg.get('fallback') or {}
    fbmeta = cfg.get('fallback_meta') or {}

    # 长 pattern 优先，避免 ch2_2_5_1 被 ch2_2_5* 之外的短规则抢走
    rules = []
    for b in blocks:
        for p in b.get('patterns') or []:
            rules.append((p, b['name']))
    rules.sort(key=lambda x: len(x[0]), reverse=True)

    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = list(db.execute("select script, chapter, title, place from scenes"))
    order = {}
    op = os.path.join(BASE, 'data', 'scene_order.json')
    if os.path.exists(op):
        order = json.load(open(op, encoding='utf-8'))
    arcs = {}
    ap = os.path.join(BASE, 'data', 'arcs.json')
    if os.path.exists(ap):
        arcs = json.load(open(ap, encoding='utf-8'))
    arc_sc = (arcs.get('scene') or {})
    chapter_map = (arcs.get('chapter_map') or {})

    def arc_of(script, chapter):
        if script in arc_sc:
            return arc_sc[script]
        return chapter_map.get(chapter or '', '')

    of = {}
    members = {}
    for r in rows:
        sc = r['script']
        name = None
        for pat, bn in rules:
            if fnmatch.fnmatchcase(sc, pat):
                name = bn
                break
        if not name:
            a = arc_of(sc, r['chapter'])
            name = fallback.get(a) or fallback.get(r['chapter'] or '') or '其他'
        of[sc] = name
        members.setdefault(name, []).append(sc)

    meta = {}
    for b in blocks:
        meta[b['name']] = {'arc': b.get('arc') or '', 'place': b.get('place') or '',
                           'order': b.get('order') or 500, 'patterns': b.get('patterns') or []}
    for bn in members:
        if bn not in meta:
            m = fbmeta.get(bn) or {}
            meta[bn] = {'arc': m.get('arc') or '', 'place': m.get('place') or '',
                        'order': m.get('order') or 800, 'patterns': []}

    # 支线按人物线细分（说话人占比）
    sp_cfg = cfg.get('support_split') or {}
    if sp_cfg:
        alias = {}
        roster = sp_cfg.get('roster') or {}
        for _ln, _names in roster.items():
            for _nm in _names:
                alias[_nm] = _ln
        ignore = set(sp_cfg.get('ignore') or [])
        src_blocks = sp_cfg.get('source_blocks') or []
        minl = sp_cfg.get('min_lines') or 2
        minr = sp_cfg.get('min_ratio') or 0.35
        rest = sp_cfg.get('rest_name') or '支线·其他'
        cand = []
        for _b in src_blocks:
            cand += list(members.get(_b, []))
        if cand:
            q = ','.join('?' * len(cand))
            counts = {}
            for _sc, _sp, _n in db.execute(
                    "select script,speaker,count(*) from lines where script in (%s) "
                    "and speaker<>'' group by script,speaker" % q, cand):
                counts.setdefault(_sc, []).append((_sp, _n))
            for _sc in cand:
                per_line = {}
                tot = 0
                for _sp, _n in counts.get(_sc, []):
                    if _sp in ignore:
                        continue
                    tot += _n
                    _ln = alias.get(_sp)
                    if _ln:
                        per_line[_ln] = per_line.get(_ln, 0) + _n
                best, bestn = '', 0
                for _ln, _n in per_line.items():
                    if _n > bestn:
                        best, bestn = _ln, _n
                if best and bestn >= minl and tot and bestn / tot >= minr:
                    target = best
                else:
                    target = rest
                for _b in src_blocks:
                    if _sc in members.get(_b, []):
                        members[_b].remove(_sc)
                members.setdefault(target, []).append(_sc)
                of[_sc] = target
            for _i, _ln in enumerate(list(roster) + [rest]):
                if _ln in members:
                    meta[_ln] = {'arc': '支线', 'place': '',
                                 'order': 910 + _i * 2, 'patterns': []}

    # 按地点/事件族细分（可多批）
    for _pc in (cfg.get('place_splits') or []):
        _srcb = _pc.get('source_blocks') or []
        _prefix = _pc.get('prefix') or '其他·'
        _restp = _pc.get('rest_name') or '其他·杂项'
        _cand = []
        for _b in _srcb:
            _cand += list(members.get(_b, []))
        if not _cand:
            continue
        _place = {}
        for _sc, _pl in db.execute("select script, place from scenes"):
            _place[_sc] = (_pl or '').strip()
        _alias = _pc.get('alias') or {}
        _family = _pc.get('family') or {}
        _groups = {}
        for _sc in _cand:
            for _b in _srcb:
                if _sc in members.get(_b, []):
                    members[_b].remove(_sc)
            _pl = _place.get(_sc) or ''
            if _pl:
                _base = _pl.split('-')[0]
                _base = _alias.get(_base, _base)
                _nm = _prefix + _base
            else:
                _pfx = _sc.split('_')[0]
                _nm = _prefix + (_family.get(_pfx) or '杂项')
            if _nm == _prefix:
                _nm = _restp
            _groups.setdefault(_nm, []).append(_sc)
        for _nm, _scs in _groups.items():
            members.setdefault(_nm, [])
            for _sc in _scs:
                if _sc not in members[_nm]:
                    members[_nm].append(_sc)
                of[_sc] = _nm
        for _i, _nm in enumerate(sorted(_groups)):
            meta[_nm] = {'arc': '其他', 'place': _nm.split('·', 1)[-1] if '·' in _nm else '',
                         'order': 930 + _i, 'patterns': []}

    # 杂项再按剧本族细分，用首场标题命名
    _fsc = cfg.get('family_split') or {}
    if _fsc:
        _fsrc = _fsc.get('source_blocks') or []
        _fpre = _fsc.get('prefix') or ''
        _maxn = _fsc.get('max_name') or 14
        _fcand = []
        for _b in _fsrc:
            _fcand += list(members.get(_b, []))
        if _fcand:
            _tit = {}
            for _sc, _t in db.execute("select script, title from scenes"):
                _tit[_sc] = _t or ''
            _fg = {}
            for _sc in _fcand:
                for _b in _fsrc:
                    if _sc in members.get(_b, []):
                        members[_b].remove(_sc)
                _fam = _sc.split('_')[0]
                _fg.setdefault(_fam, []).append(_sc)
            _small = []
            for _fam, _scs in _fg.items():
                _scs.sort(key=lambda s: (order.get(s, 99999), natkey(s)))
                if len(_scs) < (_fsc.get('min_count') or 1):
                    _small.extend(_scs)
                    continue
                _t0 = (_tit.get(_scs[0]) or '').strip() or _fam
                _nm = _fpre + _t0[:_maxn]
                _n = 2
                while _nm in members:
                    _nm = _fpre + _t0[:_maxn] + "(%d)" % _n
                    _n += 1
                members[_nm] = _scs
                for _sc in _scs:
                    of[_sc] = _nm
                meta[_nm] = {'arc': '其他', 'place': '',
                             'order': 960 + len(meta), 'patterns': []}
            if _small:
                _small.sort(key=lambda s: (order.get(s, 99999), natkey(s)))
                _nm = _fsc.get('rest_name') or '杂项·短篇'
                members[_nm] = _small
                for _sc in _small:
                    of[_sc] = _nm
                meta[_nm] = {'arc': '其他', 'place': '',
                             'order': 990, 'patterns': []}

    # 剧情段不跨单元：同一段内的场景归到多数单元（不拉出人工主线/路线单元）
    try:
        _sgp = os.path.join(BASE, 'data', 'story_segments.json')
        if os.path.exists(_sgp):
            _seg_of = json.load(open(_sgp, encoding='utf-8')).get('seg_of') or {}
            _groups2 = {}
            for _sc, _g in _seg_of.items():
                if _sc in of:
                    _groups2.setdefault(_g, []).append(_sc)
            _fixed = 0
            for _g, _scs in _groups2.items():
                _bs = [of[s] for s in _scs]
                _uniq = list(dict.fromkeys(_bs))
                if len(_uniq) < 2:
                    continue
                # 有人工单元（order<900）参与就不动
                if any((meta.get(b) or {}).get('order', 999) < 900 for b in _uniq):
                    continue
                _cnt = collections.Counter(_bs)
                _win = _cnt.most_common(1)[0][0]
                for s in _scs:
                    if of[s] != _win:
                        of[s] = _win
                        _fixed += 1
            if _fixed:
                print('剧情段跨单元归并：%d 场' % _fixed)
    except Exception as _e:
        print('段归并跳过:', _e)

    out_blocks = []
    for bn, scs in members.items():
        if not scs:
            continue
        scs.sort(key=lambda s: (order.get(s, 99999), natkey(s)))
        m = meta[bn]
        out_blocks.append({
            'name': bn, 'arc': m['arc'], 'place': m['place'], 'order': m['order'],
            'count': len(scs), 'scenes': scs,
            'first': scs[0] if scs else '', 'last': scs[-1] if scs else '',
        })
    out_blocks.sort(key=lambda b: (b['order'], b['name']))

    of_block = {b['name']: b for b in out_blocks}
    # 阶段补充：arcs.json 里没有登记的场景，按所属剧情单元的阶段补上
    arc_fix = {}
    for sc in of:
        if sc in arc_sc:
            continue
        bn = of[sc]
        a = (meta.get(bn) or {}).get('arc') or ''
        if a and a not in ('不限时间', '支线', '角色线', '其他'):
            arc_fix[sc] = a
    json.dump(arc_fix, open(os.path.join(BASE, 'data', 'arc_scene_fix.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    json.dump({'blocks': out_blocks, 'of': of, 'meta': meta},
              open(OUTP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('剧情单元', len(out_blocks), '个 / 覆盖场景', len(of))
    for b in out_blocks:
        print('  %-16s %-10s %-8s %4d 场  %s' % (
            b['name'], b['arc'], b['place'] or '-', b['count'], b['first']))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
