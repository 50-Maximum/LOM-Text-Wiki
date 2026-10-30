# -*- coding: utf-8 -*-
"""给 build_wiki2.py 接入：人工指定地点、回忆/梦境标注、场景标题覆盖。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

if "PLACE_MANUAL" not in s:
    a = "\ndef place_of(script):\n    _ov = PLACE_OVERRIDE.get(script)"
    assert a in s, "锚点1缺失"
    add = '''
# 人工逐场指定的地点（data/place_manual.json）
PLACE_MANUAL = {}
PLACE_NOTE = {}
try:
    _pmp = os.path.join(BASE, "data", "place_manual.json")
    if os.path.exists(_pmp):
        PLACE_MANUAL = json.load(open(_pmp, encoding="utf-8"))
        for _k9, _v9 in PLACE_MANUAL.items():
            if _v9.get("note"):
                PLACE_NOTE[_k9] = _v9["note"]
except Exception:
    PLACE_MANUAL = {}

# 场景标题覆盖（data/title_override.json）
TITLE_OVR = {}
try:
    _top9 = os.path.join(BASE, "data", "title_override.json")
    if os.path.exists(_top9):
        TITLE_OVR = json.load(open(_top9, encoding="utf-8"))
except Exception:
    TITLE_OVR = {}


def place_of(script):
    _mn = PLACE_MANUAL.get(script)
    if _mn is not None:
        if _mn.get("note"):
            return "", ""
        _pv9 = pcanon(_mn.get("place") or "")
        return _pv9, ("人工指定" if _pv9 else "")
    _ov = PLACE_OVERRIDE.get(script)'''
    s = s.replace(a, add, 1)
    print("place_of 接入人工指定")

if "TITLE_OVR.items()" not in s:
    a2 = """scenes = {r[0]: {"title": r[1], "chapter": r[2], "lines": r[3], "place": r[4]}
          for r in c.execute("select script,title,chapter,line_count,place from scenes")}"""
    assert a2 in s, "锚点2缺失"
    s = s.replace(a2, a2 + """
for _k8, _v8 in TITLE_OVR.items():
    if _k8 in scenes:
        scenes[_k8]["title"] = _v8""", 1)
    print("标题覆盖已接入")

if "PLACE_NOTE.get(script)" not in s:
    a3 = """    if parts:
        secs.append({"h": "出场人物", "people": [{"name": p, "n": n} for p, n in parts.most_common(14)]})"""
    assert a3 in s, "锚点3缺失"
    s = s.replace(a3, """    if PLACE_NOTE.get(script):
        secs[0]["html"] += f"场景性质：{PLACE_NOTE[script]}。"
""" + a3, 1)
    print("回忆/梦境标注已接入")

open(S, "w", encoding="utf-8").write(s)
print("done")
