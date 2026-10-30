# -*- coding: utf-8 -*-
"""发布脚本改到 v0.7 目录，并支持 GitHub Release 附件地址生成。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_release.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

s = s.replace('SRC = os.path.join(BASE, "dist_build_v06", "活侠传追踪Wiki")',
              'SRC = os.path.join(BASE, "dist_build_v07", "活侠传追踪Wiki")')
s = s.replace('"url": "https://你的下载地址/%s.zip" % NAME,',
              '"url": _url,')
s = s.replace('VER = str(json.load(open(os.path.join(BASE, "version.json"), encoding="utf-8"))["version"])',
              'VER = str(json.load(open(os.path.join(BASE, "version.json"), encoding="utf-8"))["version"])\n'
              'CFG = {}\n'
              'try:\n'
              '    CFG = json.load(open(os.path.join(BASE, "data", "update.json"), encoding="utf-8"))\n'
              'except Exception:\n'
              '    CFG = {}\n'
              'GH = CFG.get("github") or {}\n'
              '_url = ("https://github.com/%s/%s/releases/download/v%s/%s.zip"\n'
              '        % (GH.get("owner"), GH.get("repo"), VER, NAME))\n'
              'if not GH.get("owner") or not GH.get("repo"):\n'
              '    _url = "https://github.com/OWNER/REPO/releases/download/v%s/%s.zip" % (VER, NAME)')
s = s.replace('"notes": "首次内测版本。",', '"notes": "0.7.0：阶段判定改为章节＋旗标＋原文，事件跨阶段清零；分支选项可点；新增 GitHub 自动更新。",')
s = s.replace('"date": "2026-10-27",', '"date": "2026-10-28",')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("build_release.py 已更新到 v0.7")
