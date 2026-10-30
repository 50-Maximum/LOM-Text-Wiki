# -*- coding: utf-8 -*-
"""对参考 wiki 提出的门派修正，逐人回到游戏原文找证据。"""
import io, sys, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
TARGETS = {
    "无相祖师": "千灯楼", "刘颚": "泥教", "晁和": "岭南", "赵逵": "青城",
    "龙渊": "丐帮", "郝大通": "全真", "阎罗生": "崆峒", "袁乘风": "峨嵋",
    "千金叟": "丐帮", "林志恒": "岭南", "陈倔": "岭南", "李仁友": "极乐",
    "李元弃": "极乐", "火闪电": "崆峒", "叶云啾": "点苍", "阿叔": "丐帮",
    "孟瞋": "崆峒", "唐鹿": "唐门", "温无畏": "峨嵋", "明玉": "锦香",
    "阮蛋": "岭南", "米欧宽": "岭南", "觉慧": "嵩山", "觉醒": "嵩山",
}
KEYS = ("弟子", "门人", "长老", "掌门", "帮主", "法王", "护法", "真人", "道长",
        "师兄", "师姐", "师太", "门下", "出身", "拜入", "投靠", "教主", "掌派")
for nm, sect in TARGETS.items():
    rows = c.execute("select script,seq,speaker,text from lines where text like ? limit 60",
                     ("%" + nm + "%",)).fetchall()
    hit = []
    for sc, sq, sp, tx in rows:
        for k in KEYS:
            m = re.search(r".{0,14}" + k + r".{0,14}", tx)
            if m and (sect in tx or k in tx):
                hit.append("[%s#%s] %s" % (sc, sq, tx[:90].replace("\n", " ")))
                break
        if len(hit) >= 2:
            break
    print("\n### %s（参考：%s，台词 %d 句）" % (nm, sect, len(rows)))
    for h in hit:
        print("   ", h)
    if not hit:
        print("    （无门派关键词上下文）")
