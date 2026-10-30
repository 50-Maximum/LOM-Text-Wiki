# -*- coding: utf-8 -*-
"""抽出 wiki.html 的 <script> 内容，用 node --check 校验语法。"""
import io, os, re, subprocess, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
h = open(os.path.join(BASE, "web", "wiki.html"), encoding="utf-8").read()
blocks = re.findall(r"<script>(.*?)</script>", h, re.S)
print("script 块", len(blocks), [len(b) for b in blocks])
tmp = os.path.join(BASE, "data", "_check.js")
open(tmp, "w", encoding="utf-8").write("\n;\n".join(blocks))
r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
print("returncode", r.returncode)
print((r.stdout or "")[:800])
print((r.stderr or "")[:2000])
