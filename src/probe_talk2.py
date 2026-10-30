# -*- coding: utf-8 -*-
"""①取 Ch_6_6_2_Break_01_008 的可读条件 ②全库统计 talk[] 菜单写法"""
import io, sys, gzip, json, os, re, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
d = json.loads(gzip.open(os.path.join(B, "data", "mod_res", "LOMAssistant.conditions.json.gz"), "rb")
               .read().decode("utf-8"))
print("Conditions[Ch_6_6_2_Break_01_008] =",
      d["Conditions"].get("Ch_6_6_2_Break_01_008"))
print("Switches[Ch_6_6_2_Break_01_008] =",
      json.dumps(d["Switches"].get("Ch_6_6_2_Break_01_008"), ensure_ascii=False)[:300])

RAW = os.path.join(B, "data", "raw", "scripts")
RE_TALK = re.compile(r"^\s*(talk|option_\w*)\s*\[\s*(\d+)\s*\]\s*=\s*(.+)$")
pat_plain = re.compile(r'^"(\w+)\+([^"+]+)\+')
pat_cond = re.compile(r"^(\w+)\s+and\s+\"(\w+)\+([^\"+]+)\+[^\"]*\"")
kind = collections.Counter()
scripts_with = set()
files = glob.glob(os.path.join(RAW, "*.txt"))
for f in files:
    try:
        lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
    except Exception:
        continue
    for ln in lines:
        m = RE_TALK.match(ln)
        if not m:
            continue
        rhs = m.group(3).strip()
        p1 = pat_plain.match(rhs)
        p2 = pat_cond.match(rhs)
        if p2:
            kind["条件选项"] += 1
            scripts_with.add(os.path.basename(f)[:-4])
        elif p1:
            kind["无条件选项"] += 1
            scripts_with.add(os.path.basename(f)[:-4])
        else:
            kind["其他写法"] += 1
print("\n全库:", dict(kind), "｜涉及剧本", len(scripts_with), "/", len(files))
