# -*- coding: utf-8 -*-
"""角色总表 vs 页面：找出有名字却没建页的、以及该隐藏的无名 NPC。"""
import io, sys, sqlite3, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

# 1) 游戏角色表
chars = {}
for ln in open(B + r"\data\raw\system\Character_zh-cn.txt", encoding="utf-8-sig"):
    m = re.match(r"Character/([^=\s]+)\s*=\s*(.*)", ln.strip())
    if m:
        chars[m.group(1)] = m.group(2).strip()
titles = {}
for ln in open(B + r"\data\raw\system\CharacterTitle_zh-cn.txt", encoding="utf-8-sig"):
    m = re.match(r"CharacterTitle/([^=\s]+)\s*=\s*(.*)", ln.strip())
    if m:
        titles[m.group(1)] = m.group(2).strip()
print("角色键 %d，称号键 %d（非空 %d）" % (len(chars), len(titles),
      sum(1 for v in titles.values() if v and v != "{title}")))

# 2) 说话统计（按 speaker 名）
spk = collections.Counter()
for nm, k in c.execute("""select speaker,count(*) from lines
                          where speaker<>'' group by 1 order by 2 desc"""):
    spk[nm] = k

# 3) 页面名（人物）
pages = {r[0].split("·")[-1]: r[0] for r in
         c.execute("select slug from pages where type='人物'")}
alias = {r[0]: r[1] for r in c.execute("select alias,slug from aliases")}

cand = []
for k, nm in chars.items():
    if not nm or nm in ("？？？", "无名", "██", "{title}"):
        continue
    if nm in pages or nm in alias:
        continue
    cand.append((spk.get(nm, 0), nm, k, titles.get(k, "")))
cand.sort(key=lambda x: -x[0])
print("\n=== 角色表里有、但没有页面的名字（%d 个），按台词数：" % len(cand))
for n, nm, k, ti in cand:
    print("  %-12s 台词 %-4d %-14s %s" % (nm, n, k, ("［称号 " + ti + "］") if ti else ""))
