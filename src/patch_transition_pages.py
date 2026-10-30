# -*- coding: utf-8 -*-
"""给 0 句剧本建「转场节点」页：只写它做什么、谁指向它、它指向谁，不编任何叙述。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''for script, sc in scenes.items():
    if (sc.get("lines") or 0) <= 0:
        continue'''
if "_TL = {" not in s:
    s = s.replace("for script, sc in scenes.items():",
                  '_TL = {"main": "继续", "branch": "分支", "ending": "结局", "map": "回地图",\n'
                  '       "story": "转段", "travel": "赶路", "temp": "临时", "scene": "转场"}\n'
                  'for script, sc in scenes.items():', 1)
new = '''for script, sc in scenes.items():
    if (sc.get("lines") or 0) <= 0:
        _slug = f"场景/{script}"
        _nxt, _rows = [], []
        try:
            for _d, _ty in c.execute("select dst,type from scene_edges where src=? order by type, dst", (script,)):
                _t = scenes.get(_d, {}).get("title") or _d
                _rows.append({"note": _TL.get(_ty, _ty) + "：" + _t, "quote": "",
                              "script": _d if _d in scenes else "", "title": _t,
                              "seq": 0, "routes": []})
                if not _nxt and _d in scenes and (scenes[_d].get("lines") or 0) > 0:
                    _nxt.append(_t)
        except Exception:
            pass
        _in = []
        try:
            for (_s0,) in c.execute("select src from scene_edges where dst=? order by src", (script,)):
                _t = scenes.get(_s0, {}).get("title") or _s0
                _in.append({"note": _t, "quote": "", "script": _s0 if _s0 in scenes else "",
                            "title": _t, "seq": 0, "routes": []})
        except Exception:
            pass
        _nm = "转场节点" + (("接「%s」" % _nxt[0]) if _nxt else "") + " " + script
        _secs = [{"h": "场景信息",
                  "html": "转场节点（本场无台词，不涉及场所）。" + arc_of(script) + "。"}]
        if _rows:
            _secs.append({"h": "接下来", "rows": _rows})
        if _in:
            _secs.append({"h": "被指向", "rows": _in})
        add_page(_slug, "场景", _nm,
                 "本场没有台词，是剧本之间的转场与判定节点，只做跳转与开关设置。",
                 {"脚本": script, "阶段": arc_of(script), "类型": "转场节点"},
                 _secs, ["场景", arc_of(script)], 0, [arc_of(script)],
                 sort_key=script, facet=arc_of(script), facet2=ROUTEOF.get(script, ""))
        continue'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("转场节点页已接入")
