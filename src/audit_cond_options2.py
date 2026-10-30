# -*- coding: utf-8 -*-
"""补充审计：①内联声明的选项表 ②choose 带第二个参数 ③菜单启用条件痕迹。"""
import io, sys, os, re, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
files = sorted(glob.glob(os.path.join(RAW, "*.txt")))

inline = collections.Counter()
n_inline_blocks = 0
choose2 = []
kw = collections.Counter()

RE_INLINE = re.compile(r"^\s*local\s+(option_\w+)\s*=\s*\{(.+)\}\s*$")
RE_CHOOSE2 = re.compile(r"choose\s*\(\s*(option_\w+)\s*,\s*([^)]+)\)")
KEYS = ("require", "condition", "unlock", "enable", "disable", "CanUse", "isvalid", "checkcond")

for f in files:
    script = os.path.basename(f)[:-4]
    for ln in open(f, encoding="utf-8", errors="replace"):
        m = RE_INLINE.match(ln)
        if m and m.group(2).strip():
            n_inline_blocks += 1
            for k in re.findall(r"[\"']([^\"']+)[\"']", m.group(2)):
                inline[k] += 1
        c2 = RE_CHOOSE2.search(ln)
        if c2:
            choose2.append((script, ln.strip()[:120]))
        low = ln.lower()
        for k in KEYS:
            if k.lower() in low:
                kw[k] += 1

print("内联选项表块 %d 个，内联选项 %d 条" % (n_inline_blocks, sum(inline.values())))
print("choose 带第二参数 %d 处" % len(choose2))
for x in choose2[:8]:
    print("   ", x[0], "|", x[1])
print("\n关键字出现次数：", dict(kw))
