# -*- coding: utf-8 -*-
"""扫描正文，给没有地点字段的场景回填地点；同时统计时间词。"""
import sqlite3, re, collections

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row

PLACES = ["飞天殿", "夺魄森林", "铁拳巷", "玄功洞", "夺魄峰", "无色广场",
          "常风观", "上清宫", "青城山镇", "唐门", "后山", "伙房", "炼丹房",
          "正心堂", "讲经堂", "锻冶场", "大门", "男弟子房", "女弟子房",
          "闹市", "外堡", "茶肆", "药铺", "义田", "温泉", "练功场", "练功塔",
          "夺魄", "青城", "崆峒", "唐家堡", "锦香宫", "南宫世家", "飞石帮"]

TIME = ["初一", "十五", "月初", "月末", "翌日", "次日", "当晚", "隔日",
        "清晨", "晌午", "黄昏", "深夜", "三更", "开春", "入夏", "秋末", "寒冬",
        "三月", "五月", "八月", "十月", "腊月", "岁末", "年初"]

scenes = [dict(r) for r in c.execute("SELECT script, place FROM scenes WHERE line_count>0")]
by_script = collections.defaultdict(list)
for r in c.execute("SELECT script, text FROM lines"):
    by_script[r["script"]].append(r["text"] or "")

filled = 0
dist = collections.Counter()
samples = []
for sc in scenes:
    if sc["place"]:
        continue
    txt = "\n".join(by_script.get(sc["script"], []))
    cnt = collections.Counter()
    for p in PLACES:
        n = txt.count(p)
        if n:
            cnt[p] = n
    if cnt:
        best, n = cnt.most_common(1)[0]
        if n >= 2 or best in ("飞天殿", "常风观", "上清宫", "青城山镇", "无色广场", "铁拳巷", "玄功洞", "夺魄峰", "夺魄森林"):
            c.execute("UPDATE scenes SET place=? WHERE script=?", (best, sc["script"]))
            filled += 1
            dist[best] += 1
            if len(samples) < 8:
                samples.append((sc["script"], best, n))
c.commit()

print("回填场景:", filled)
print("分布:", dist.most_common(15))
print("样例:", samples)

print("\n=== 时间词出现次数（全库） ===")
alltxt = "\n".join(t for v in by_script.values() for t in v)
tc = [(w, alltxt.count(w)) for w in TIME]
print([x for x in tc if x[1]])

# 战斗结果分支抽样
print("\n=== 战斗结果分支抽样 ===")
rows = c.execute("""SELECT script, branch FROM branches
                    WHERE branch LIKE '%Battle_Result%' OR branch LIKE '%Combat_Result%'
                    LIMIT 6""").fetchall()
for r in rows[:4]:
    print("  ", r["script"], "|", r["branch"])
