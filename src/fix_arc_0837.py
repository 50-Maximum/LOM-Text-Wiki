# -*- coding: utf-8 -*-
"""修正：比武招亲放回武林大会之前；序章不整章归武林盟；三人道中遇敌改为「同行者只有一人」。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


arcs = load("arcs.json")
arcs["arcs"] = ["外姓弟子", "南宫寿宴", "江陵围城", "唐门衰败", "比武招亲",
                "武林大会", "武林盟进攻唐门", "不限时间"]
arcs["chapter_map"]["第0章"] = "外姓弟子"
sc = arcs.setdefault("scene", {})
sc.pop("ch0_5", None)
sc["ch0_5"] = "武林盟进攻唐门"
sc["ch0_6"] = "武林盟进攻唐门"
save("arcs.json", arcs)
print("阶段顺序：…唐门衰败 → 比武招亲 → 武林大会 → 武林盟进攻唐门")
print("第0章 → 外姓弟子（整章不再归武林盟）；仅 ch0_5/ch0_6 单独归武林盟进攻唐门")

patch = load("notes_patch.json")
patch.setdefault("travel_result_401_501", {})["三人道中遇敌拦路"] = {
    "note": "卧云岗返程路上，因先前卧云岗的选择，同行者只有龙湘与福韫中的一人；"
            "途中遇敌拦路，出手的是同行的那一位。"}
patch.setdefault("travel_result_401_504", {})["三人道中遇敌拦路"] = {
    "note": "卧云岗返程路上，因先前卧云岗的选择，同行者只有龙湘与福韫中的一人；"
            "途中遇敌索命，由同行的那一位接战。"}
save("notes_patch.json", patch)
print("三人道中遇敌：改为「同行者二择一」")
