# -*- coding: utf-8 -*-
"""应用 B 组核查结果（21 人）。暂不重建，等 A 组回来一并重建。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


PREFIX = {
    "梁有诗": "金国",
    "楚掌柜": "市井",
    "王五": "夺魄门",
    "红篷王": "朝廷",
    "耿怔忡": "夺魄门",
    "邓老爹": "铁拳门",
    "钟老爷": "市井",
    "霍郎": "峨嵋派",
    "马帮主": "丐帮",
    "龙渊": "丐帮",
}
cp = load("chars_prefix.json")
cp.update(PREFIX)
save("chars_prefix.json", cp)
print("B 组归属写入 %d 条" % len(PREFIX))

cf = load("chars_fix.json")
cf.setdefault("merge", {})["瑞公子"] = "瑞笙"
save("chars_fix.json", cf)
print("并义 瑞公子 → 瑞笙")

# 备注：邓老爹与先掌门邓夷
ic = load("intros_char.json")
node = ic.get("人物/邓老爹")
if isinstance(node, dict):
    t = node.get("text") or ""
    note = "邓老爹是崆峒派铁拳门先掌门邓夷。"
    if note not in t:
        node["text"] = note + t
        save("intros_char.json", ic)
        print("邓老爹导语已补一句")

# 未定 8 人列出备查
print("\n仍留江湖（原文无门派）：毕逢、水德、玄冥老祖、破戒僧、陈裕光、鞠兰")
print("保持江湖（确属散人）：木仙姑、牛长寿、谭霸刀、齐壬")
