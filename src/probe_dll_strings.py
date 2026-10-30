# -*- coding: utf-8 -*-
import io, sys, os, re, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
MD = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\Managed"
CJK = re.compile(r"[\u4e00-\u9fff]")
KW = ("触发", "条件", "好感", "贡献", "心相", "行动点", "前置")
for p in sorted(glob.glob(os.path.join(MD, "*.dll"))):
    nm = os.path.basename(p)
    raw = open(p, "rb").read()
    # .NET #US 堆是 UTF-16LE
    strs = re.findall(rb"(?:[\x20-\x7e\x00-\xff]{0,0})", b"")
    try:
        txt = raw.decode("utf-16-le", errors="ignore")
    except Exception:
        continue
    hits = [s for s in KW if s in txt]
    if hits:
        # 提取含关键词的片段
        samples = []
        for k in hits:
            i = txt.find(k)
            seg = txt[max(0, i - 40): i + 60].replace("\x00", "")
            samples.append((k, re.sub(r"[\x00-\x1f]", "", seg)))
        print("== %-24s %8d 字节  命中 %s" % (nm, len(raw), ",".join(hits)))
        for k, s in samples[:3]:
            print("     [%s] %s" % (k, s[:100]))
