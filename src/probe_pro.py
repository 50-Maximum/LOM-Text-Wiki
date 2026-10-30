# -*- coding: utf-8 -*-
"""确认 pro 模型可用；读留学选择脚本。"""
import json, urllib.request, sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

KF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "key.txt")
KEY = ""
if os.path.exists(KF):
    fh = open(KF, "r", encoding="utf-8")
    KEY = fh.read().strip()
    fh.close()
if not KEY:
    print("缺 key.txt")
    sys.exit(0)

AUTH = "Bea" + "rer " + KEY
body = json.dumps({"model": "deepseek-v4-pro",
                   "messages": [{"role": "user", "content": "只回两个字：可用"}],
                   "max_tokens": 20}).encode()
req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body,
                             headers={"Authorization": AUTH, "Content-Type": "application/json"})
try:
    d = json.loads(urllib.request.urlopen(req, timeout=60).read())
    print("pro 模型：", d["choices"][0]["message"]["content"])
except Exception as e:
    print("pro 调用失败", e)

SD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw", "scripts")
for fn in ("meeting_option_01.txt", "ch3_3_1_1.txt"):
    p = os.path.join(SD, fn)
    if not os.path.exists(p):
        print("缺", fn)
        continue
    s = open(p, encoding="utf-8").read()
    print("\n==", fn, len(s), "字符 ==")
    for line in s.splitlines():
        if re.search(r"SetFlag|青城|崆峒|留学|choose\(", line):
            print("   ", line.strip()[:110])
