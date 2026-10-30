# -*- coding: utf-8 -*-
"""山村野店查证结论：不是固定地点，是行旅途中的乡野小店；简介整段重写。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\place_edits.json"
E = json.load(open(p, encoding="utf-8"))
E.setdefault("intro", {})["山村野店"] = (
    "山村野店是行旅途中供人歇脚、吃些乡野饭食的小店，并非某一州县的固定去处。"
    "赵活与小梅同行时曾途经一家山村野店，尝了当地风味小吃；唐门师兄弟也曾聚在"
    "这样的山村小店里吃面喝酒唱山歌。原文没有交代这些店分属何地。")
E.setdefault("type", {})["山村野店"] = "街市店肆"
E.setdefault("region", {})["山村野店"] = "其他"
json.dump(E, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("山村野店：简介重写、类型=街市店肆、区域=其他")
