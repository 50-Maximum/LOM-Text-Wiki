# -*- coding: utf-8 -*-
"""生成称号表 + 无名群像隐藏表 + 变体合并。"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"

chars = {}
for ln in open(B + r"\data\raw\system\Character_zh-cn.txt", encoding="utf-8-sig"):
    m = re.match(r"Character/([^=\s]+)\s*=\s*(.*)", ln.strip())
    if m:
        chars[m.group(1)] = m.group(2).strip()

title = {}
for ln in open(B + r"\data\raw\system\CharacterTitle_zh-cn.txt", encoding="utf-8-sig"):
    m = re.match(r"CharacterTitle/([^=\s]+)\s*=\s*(.*)", ln.strip())
    if not m:
        continue
    k, t = m.group(1), m.group(2).strip()
    if not t or t == "{title}":
        continue
    nm = chars.get(k) or chars.get(re.sub(r"_\d+$", "", k))
    if not nm:
        continue
    title.setdefault(nm, t)
json.dump(title, open(B + r"\data\chars_title.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("称号 %d 人：" % len(title), "、".join("%s=%s" % (k, v) for k, v in title.items()))

# 无名群像（隐藏，不给列表露面，但页面与链接保留）
hidden = """路人 歹人 众人 女子 婢女 刺客 老人 宾客 家丁 书生 童生 女童 男童
少年 少女 妇人 乞丐 老乞丐 店小二 掌柜 店家娘子 官兵 老将军 海盗 山贼 捕快
知县 通判 先生 武师 武师众 女侠 少侠 公子侠 蒙面人 大夫 军医 女乐 商人
轿中人 回音 鬼卒 牛头 马面 铜人 醉汉 樵夫 金士兵 蒙古兵 蒙古摔角手
西夏士兵 大理士兵 吐蕃士兵 绝世高手 仙姑 大妈 娘 爹 昆仑奴 虎战车 崆峒四姝
唐门众弟子 飞石帮众 武林盟群侠 鸡 狗 蛇 猴子 野猪 马 狼 鹦鹉 女飞贼
唐门弟子 唐门女弟子 青城弟子 峨嵋弟子 峨嵋女弟子 点苍弟子 点苍女弟子
嵩山弟子 全真弟子 全真长老 铁拳弟子 铁拳老弟子 夺魄弟子 玄功弟子
飞天弟子 飞天女弟子 锦香弟子 雪山弟子 岭南弟子 岭南女弟子 泥教弟子 沧帮弟子
飞石帮 南宫家丁 南宫妇人 南宫老人 唐门掌门 掌门 长老 前任掌门 帮主夫人
铁拳前掌门 夺魄掌门 玄功掌门 点苍双尊 七星剑主 岭南七星剑主 剑圣 点苍剑圣
马帮主 毛帮主 王帮主 石帮主 雷掌门 向掌门 姚掌门 邹掌门 唐掌门 唐门掌门
昆仑奴 说书先生 何大妈 朱婶 孙婶 孙娘子 费娘子 乐娘子 乐屏娘子 管帐先生
牛长寿 邓老爹 大眼锥 火闪电 鹤手 王五 老陈 老孟 柳叔 阿金 阿牛 秀秀 雉儿""".split()
hidden = sorted({h for h in hidden if h})
json.dump(hidden, open(B + r"\data\chars_hidden.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("隐藏 %d 个无名条目" % len(hidden))

# 变体合并
p = B + r"\data\chars_fix.json"
d = json.load(open(p, encoding="utf-8"))
M = d.setdefault("merge", {})
add = {
    "白衣少年": "瑞笙", "玄衣少年": "刘颚",
    "少年唐布衣": "唐布衣", "少年唐铮": "唐铮",
    "少年赵活": "赵活", "幼年赵活": "赵活", "赵活（？）": "赵活",
    "赵活屁股": "赵活", "赵活的手": "赵活",
    "叶云舟（？）": "叶云舟", "魏菊？": "魏菊",
    "万胜": "万胜金刀",
}
n0 = len(M)
M.update(add)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("别名 %d → %d" % (n0, len(M)))
