# -*- coding: utf-8 -*-
"""核验前端已部署：脚本直达、转场提示、seq 传参。"""
import io, sys, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
h = urllib.request.urlopen("http://127.0.0.1:8765/", timeout=20).read().decode("utf-8")
print("HTML 长度:", len(h))
print("A 路由传 seq:", "renderScene(arg + (_q ? ('?' + _q) : ''))" in h)
print("B 转场提示:", "转场脚本，无台词" in h)
print("C 脚本直达卡:", "脚本直接命中" in h)
print("D 原文结果显示场景标题:", "第${l.seq}句" in h)
