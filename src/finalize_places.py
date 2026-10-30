# -*- coding: utf-8 -*-
"""收尾三件：
① 势力「金乌」删掉（是人物金乌上人，不是门派）；
② 谷底系列场景归到「唐门-谷底」；
③ build 收尾加一段：改名后残留的旧页面并入新页面（南沟 → 南沟集）。
"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

# ①
ff = os.path.join(BASE, "data", "factions_fix.json")
F = json.load(open(ff, encoding="utf-8"))
dl = F.setdefault("delete", [])
if "金乌" not in dl:
    dl.append("金乌")
    json.dump(F, open(ff, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("factions_fix：已删「金乌」势力")
else:
    print("factions_fix：金乌已在删除表")

# ②
p = os.path.join(BASE, "data", "place_override.json")
ov = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
GUDI = ["S0208_03", "S0208_04_01_04", "S0208_04_02_03", "S0208_04_03",
        "S0208_04_break_start_01", "S0208_05_01"]
for sc in GUDI:
    ov[sc] = {"place": "唐门-谷底",
              "why": "赵活与叶云裳跌落谷底后的疗伤生活（谷底即唐门禁地）"}
json.dump(ov, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("place_override：谷底 %d 场已归位，总 %d 条" % (len(GUDI), len(ov)))

# ③ build 收尾：旧页并入新页
S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()
if "_RENAMED_DONE" not in s:
    anchor = 'print("导语补注", len(PE_TIP), "处；隐藏", len(PE_HIDE), "个区域页")'
    assert anchor in s, "补注日志行未找到"
    add = anchor + '''

# 改名后残留的旧页面：内容并入新页面，旧页删除并加重定向
_RENAMED_DONE = []
for _o3, _n3 in (PE.get("rename") or {}).items():
    _so, _sn = f"地点/{_o3}", f"地点/{_n3}"
    if _so not in _idx or _sn not in _idx:
        continue
    _po, _pn = pages[_idx[_so]], pages[_idx[_sn]]
    _so_sec = _pj(_po[5], "[]")
    _sn_sec = _pj(_pn[5], "[]")
    _have2 = {x.get("h") for x in _sn_sec}
    _merged2 = _sn_sec + [x for x in _so_sec if x.get("h") not in _have2]
    _inf2 = _pj(_pn[4], "{}")
    for _k3, _v3 in _pj(_po[4], "{}").items():
        _inf2.setdefault(_k3, _v3)
    pages[_idx[_sn]] = (_pn[0], _pn[1], _pn[2],
                        _pn[3] or _po[3], json.dumps(_inf2, ensure_ascii=False),
                        json.dumps(_merged2, ensure_ascii=False), _pn[6],
                        max(_pn[7] or 0, _po[7] or 0), _pn[8], _pn[9], _pn[10],
                        _pn[11], _pn[12], _pn[13])
    pages[_idx[_so]] = (_po[0], _po[1], _po[2], _po[3], _po[4], _po[5], _po[6],
                        _po[7], _po[8], _po[9], _po[10], 1, _po[12], _po[13])
    redirects.append((_so, _sn))
    _RENAMED_DONE.append(_o3)
if _RENAMED_DONE:
    print("改名并页", len(_RENAMED_DONE), "：", "、".join(_RENAMED_DONE))
'''
    s = s.replace(anchor, add, 1)
    open(S, "w", encoding="utf-8").write(s)
    print("build_wiki2：已加改名并页收尾")
else:
    print("build_wiki2：已有改名并页")
