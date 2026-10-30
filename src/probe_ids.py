# -*- coding: utf-8 -*-
"""1) 看 speaker_id 命名是否与立绘 bundle 对得上；2) 找物品 id→图标名的定义。"""
import io, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("--- speaker_id -> 说话人（前 40）---")
for r in con.execute("""select speaker_id, speaker, count(*) n from lines
                        where speaker_id is not null and speaker_id<>''
                        group by speaker_id, speaker order by n desc limit 40"""):
    print("   %-22s %-12s %d" % (r[0], r[1], r[2]))

print("\n--- speaker_id 总数 ---")
print(con.execute("select count(distinct speaker_id) from lines").fetchone()[0])

# Lua 里找 item_food_ 之类
root = r"D:\LegendOfMortal Wiki\data\raw"
pat = re.compile(r"item_(food|medi|book|bag|card|water|special|take_money|break_food|hurt_leg)_(\d+)")
found = collections.Counter()
examples = []
for dirpath, _, files in os.walk(root):
    for f in files:
        p = os.path.join(dirpath, f)
        try:
            s = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        m = pat.findall(s)
        if m:
            for cat, num in m:
                found[cat] += 1
            if len(examples) < 6:
                i = pat.search(s)
                examples.append((f, s[max(0, i.start() - 120):i.start() + 120].replace("\n", " ")))
print("\n--- item_* 出现统计 ---", dict(found))
for f, ex in examples:
    print("\n  %s: ...%s..." % (f, ex))
