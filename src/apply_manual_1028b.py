# -*- coding: utf-8 -*-
"""第二批：清掉过期的「江湖」硬覆盖，补上漏掉的人，修岭南派方向。"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


cp = load("chars_prefix.json")
old = len(cp)
drop = [k for k, v in cp.items() if v == "江湖"]
for k in drop:
    cp.pop(k)
print("清掉硬写「江湖」的覆盖 %d 条（回落到人物归属表）" % len(drop))

cp.update({
    "岳珂": "朝廷", "乐屏": "南宫世家", "陈倔": "岭南派",
    "杨玄奇": "千灯楼", "书蓉": "杏花林", "丹霞子": "崆峒派",
    "来新子": "火炎山剑阁",
})
save("chars_prefix.json", cp)
print("补归属 %d 条，现有 %d 条" % (6, len(cp)))

cf = load("chars_fix.json")
mg = cf.setdefault("merge", {})
mg["千面人魔杨某人"] = "杨玄奇"
mg["道法将军"] = "丹霞子"
save("chars_fix.json", cf)
print("补并义 千面人魔杨某人→杨玄奇、道法将军→丹霞子")

ef = load("extra_factions.json")
ef["杏花林"] = {
    "text": "南阳杏花林是书蓉所在之处。丹霞子曾在此遇见虞小梅，虞小梅也在此许过愿。",
}
save("extra_factions.json", ef)
print("额外势力 杏花林 已加")

# 修 FAC_NORM：岭南派 现在是正式名，不能再转成岭南剑派
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")
s = s.replace('    "岭南派": "岭南剑派",\n', '    "岭南剑派": "岭南派",\n')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("FAC_NORM：岭南剑派 → 岭南派")
