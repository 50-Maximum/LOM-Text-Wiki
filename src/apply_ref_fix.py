# -*- coding: utf-8 -*-
"""按原文证据修正门派（参考 wiki 提出的差异，只采有原文支持的）。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\chars_prefix.json"
d = json.load(open(p, encoding="utf-8"))
fix = {
    "无相祖师": "千灯楼",   # 「被千灯楼无相祖师以尸心蛊操控」
    "郝大通": "全真",       # 「全真七子中的太古真人郝大通」
    "阎罗生": "崆峒",       # 「玄功门有丹青罗刹阎罗生」
    "孟瞋": "崆峒",         # 「铁拳门有白眉虎孟瞋」
    "袁乘风": "峨嵋",       # 「峨嵋叛徒…风中奇猿」
    "千金叟": "丐帮",       # 「生父是丐帮旧派的长老，人称千金叟」
    "李仁友": "极乐教",     # 「极乐教主李仁友」
    "李元弃": "极乐教",     # 「极乐教左护法」
    "阿叔": "丐帮",         # 「阿叔说俺们是旧派，是真正的丐帮」
    "林志恒": "岭南",       # 岭南场景中被称「林志恒师兄」
    "叶云啾": "点苍",
}
d.update(fix)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("前缀修正", len(fix), "人，累计覆盖", len(d))
