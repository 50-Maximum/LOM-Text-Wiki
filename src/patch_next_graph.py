# -*- coding: utf-8 -*-
"""「接下来」改用场景图（scene_edges）：分清继续、分支择一、结局、回地图。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

start = s.find('    _nxt = (NXT.get(script) or {})')
endmark = '    secs.append({"h": "接下来", "rows": _jrows})'
end = s.find(endmark)
assert start > 0 and end > start, "找不到旧的接下来块"
end += len(endmark)

new = '''    _jrows = []
    _seen_dst = set()
    _TYPE_LABEL = {"main": "继续", "branch": "分支", "ending": "结局", "map": "回地图",
                   "story": "转段", "travel": "赶路", "temp": "临时"}
    try:
        for _e in c.execute("""select dst,type,cond,switch,result,site from scene_edges
                               where src=? order by type, site, result""", (script,)):
            _dst, _ty = _e["dst"], _e["type"]
            if _ty in ("main", "branch") and _dst not in scenes:
                continue
            _key = (_ty, _dst)
            if _key in _seen_dst:
                continue
            _seen_dst.add(_key)
            _title = scenes.get(_dst, {}).get("title") or ""
            if _ty == "ending":
                _lab = "结局：GameOver（战败或剧情终止）"
            elif _ty == "map":
                _lab = "回地图（养成界面）"
            elif _ty in ("main", "branch", "story", "travel", "temp"):
                _lab = _TYPE_LABEL.get(_ty, _ty) + "：" + (_title or _dst)
                if _ty == "branch":
                    _bits = []
                    if _e["switch"]:
                        _bits.append("判定 %s 结果 %s" % (_e["switch"], _e["result"]))
                    if _e["cond"]:
                        _bits.append(_e["cond"].replace("switch", "判定")
                                     .replace("_result==", " 结果=")[:80])
                    if _bits:
                        _lab += "（" + "；".join(_bits) + "）"
            else:
                _lab = _ty + "：" + (_title or _dst)
            _jrows.append({"note": _lab, "quote": "",
                           "script": _dst if _dst in scenes else "",
                           "title": _title, "seq": 0, "routes": []})
            if len(_jrows) >= 12:
                break
    except Exception as _e:
        pass
    if not _jrows:
        _jrows.append({"note": "本场没有出向转场，结束后由上层事件或地图接续。",
                       "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
    secs.append({"h": "接下来", "rows": _jrows})'''

s = s[:start] + new + s[end:]
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("接下来已改用场景图，syntax ok")
