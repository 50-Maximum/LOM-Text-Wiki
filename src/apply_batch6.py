# -*- coding: utf-8 -*-
"""第 6 批：
1) 五零判定的 8 场（含 ch4_5_2 两地点）；
2) 新增地点「眉山镇」，挂在眉山下；
3) 下辖地点行带上明确 slug，避免跳到势力页；
4) 并义：同名既是地点又是势力的，两页共用一套内容。
"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

# ---------- 1. 覆盖表 ----------
p = os.path.join(BASE, "data", "place_override.json")
ov = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
BATCH = {
    "S8300_01_02": {"place": "唐门-弟子房", "why": "五零判定：打完飞石帮喽啰回房擦药闲聊，按弟子房计"},
    "S2321_04_02_01": {"place": "襄阳", "why": "五零判定：孟仙谣论江陵马军司与襄阳守军编制，按襄阳计"},
    "ch3_5_3_7_1": {"place": "江陵", "why": "五零判定：唐门弟子自江陵城下败退，归江陵"},
    "ch4_5_2": {"places": ["唐门-大门", "卧云岗"],
                "why": "五零判定：一段剧情跨两处——先在唐门大门别过，后在卧云岗随飞石帮同行"},
    "ch6_8_2_3_2": {"place": "风雨山", "why": "五零判定：南宫深与赵活论家事在风雨山"},
    "talk_girl5_02_06": {"place": "崆峒-夺魄森林", "why": "五零判定：夏侯兰逼上官萤代父领死在夺魄森林"},
    "pharmacy_work_501": {"place": "唐门-药铺", "why": "五零判定：坐诊场景即唐门药铺（原文亦作唐门医馆，同义）"},
    "ch2_4_4_1": {"place": "唐门-外堡", "why": "五零判定：青城峨嵋弟子在唐门外堡备行装赶赴江陵"},
}
ov.update(BATCH)
json.dump(ov, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("覆盖表 %d 条" % len(ov))

# ---------- 2. 眉山镇挂到眉山下 ----------
pf = os.path.join(BASE, "data", "places_fix.json")
P = json.load(open(pf, encoding="utf-8")) if os.path.exists(pf) else {}
par = P.setdefault("parent", {})
if par.get("眉山镇") != "眉山":
    par["眉山镇"] = "眉山"
    json.dump(P, open(pf, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("places_fix：眉山镇 → 眉山")
else:
    print("places_fix：已是眉山镇→眉山")

# ---------- 3. 改 build_wiki2 ----------
S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()

# 3a 下辖地点行带 slug
old_k = ('                krows.append({"note": k + (("｜" + kl[:44]) if kl else ""),\n'
         '                              "quote": "", "script": "", "title": k,\n'
         '                              "seq": 0, "routes": []})')
new_k = ('                krows.append({"note": k + (("｜" + kl[:44]) if kl else ""),\n'
         '                              "quote": "", "script": "", "title": k,\n'
         '                              "slug": f"地点/{k}",\n'
         '                              "seq": 0, "routes": []})')
if old_k in s and '"slug": f"地点/{k}"' not in s:
    s = s.replace(old_k, new_k, 1)
    print("build_wiki2：下辖地点行已带地点 slug")
else:
    print("build_wiki2：下辖地点行已是 slug 版或未找到")

# 3b place_of 支持多地点
old_ov = ('    _ov = PLACE_OVERRIDE.get(script)\n'
          '    if _ov is not None:\n'
          '        _pv = pcanon(_ov.get("place") or "")\n'
          '        return _pv, ("人工核定" if _pv else "证据不足")')
new_ov = ('    _ov = PLACE_OVERRIDE.get(script)\n'
          '    if _ov is not None:\n'
          '        _pls = _ov.get("places")\n'
          '        if _pls:\n'
          '            _pv = "／".join(pcanon(x) for x in _pls if pcanon(x))\n'
          '            return _pv, ("人工核定" if _pv else "证据不足")\n'
          '        _pv = pcanon(_ov.get("place") or "")\n'
          '        return _pv, ("人工核定" if _pv else "证据不足")')
if "_pls = _ov.get(\"places\")" not in s:
    assert old_ov in s, "place_of 覆盖分支未找到"
    s = s.replace(old_ov, new_ov, 1)
    print("build_wiki2：place_of 支持多点位")
else:
    print("build_wiki2：已支持多点位")

open(S, "w", encoding="utf-8").write(s)
print("done")
