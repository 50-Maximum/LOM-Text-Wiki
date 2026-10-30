# -*- coding: utf-8 -*-
"""反向核查：剧本里出现、但角色表里没有的说话人；以及称号映射可行性。"""
import io, sys, sqlite3, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

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

print("=== 说话人不在角色表里的（前 40）")
names = set(chars.values())
for sp, k in c.execute("select speaker,count(*) from lines where speaker<>'' group by 1 order by 2 desc"):
    if sp not in names:
        print("  %-12s %d" % (sp, k))

print("\n=== 称号 → 角色名（按角色键回溯）")
rev = {}
for k, t in titles.items():
    if not t or t == "{title}":
        continue
    nm = chars.get(k) or chars.get(re.sub(r"_\d+$", "", k))
    if nm:
        rev.setdefault(nm, []).append(t)
for nm, ts in rev.items():
    print("  %-8s %s" % (nm, "、".join(sorted(set(ts)))))

print("\n=== CharacterIntro 里有没有昆仑奴/万胜")
for ln in open(B + r"\data\raw\system\CharacterIntro_zh-cn.txt", encoding="utf-8-sig"):
    if ("昆仑奴" in ln) or ("万胜" in ln):
        print("  " + ln.strip()[:150])
