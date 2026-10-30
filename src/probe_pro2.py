# -*- coding: utf-8 -*-
"""重测 pro：给足 max_tokens。"""
import json, os, sys, io, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
KF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "key.txt")
fh = open(KF, "r", encoding="utf-8"); KEY = fh.read().strip(); fh.close()
AUTH = "Bea" + "rer " + KEY
body = json.dumps({"model": "deepseek-v4-pro",
                   "messages": [{"role": "user", "content": "用一句话说明：分支剧情里的互斥是什么意思。"}],
                   "max_tokens": 400}).encode()
req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body,
                             headers={"Authorization": AUTH, "Content-Type": "application/json"})
try:
    d = json.loads(urllib.request.urlopen(req, timeout=120).read())
    m = d["choices"][0]["message"]
    print("content:", (m.get("content") or "")[:200])
    print("reasoning:", (m.get("reasoning_content") or "")[:120])
    print("usage:", d.get("usage"))
except Exception as e:
    print("失败", e)
