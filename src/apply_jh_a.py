# -*- coding: utf-8 -*-
"""应用 A 组核查结果（23 人），并纠正丁侃/曹建军的误判。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


PREFIX = {
    "公主": "杏花林", "瑞杏": "杏花林", "前任掌门": "唐门", "拓拔豹": "西夏",
    "大眼锥": "市井", "孙婶": "市井",
    "丁侃": "江湖", "曹建军": "江湖",
    "万胜金刀": "江湖", "仙姑": "江湖", "余自咏": "江湖", "冯史": "江湖",
    "左思": "江湖", "幽山老祖": "江湖", "方少侠": "江湖", "方震天": "江湖",
    "易凡": "江湖", "曾文": "江湖", "成吉思汗": "江湖",
}
cp = load("chars_prefix.json")
cp.update(PREFIX)
save("chars_prefix.json", cp)
print("A 组归属写入 %d 条" % len(PREFIX))

# 方少侠就是方震天
cf = load("chars_fix.json")
cf.setdefault("merge", {})["方少侠"] = "方震天"
save("chars_fix.json", cf)
print("并义 方少侠 → 方震天")

# 丁侃/曹建军 备注：说话人标签是伪装
ic = load("intros_char.json")
for nm, note in [
    ("丁侃", "此人在 ch2_4_10_2_2 一段里，场中说话人标签多为被擒者的伪装，"
             "不能据标签定师门；原文只说他为上官世家之故落草梅州长滩为盗。"),
    ("曹建军", "他在 ch2_4_10_2_2 自称嵩山派，实为伪装；同段有「出身火炎山剑阁的叛徒」全胜利自承身份。"),
]:
    node = ic.get("人物/" + nm)
    if isinstance(node, dict):
        t = node.get("text") or ""
        if note not in t:
            node["text"] = t + note
            print("补备注：", nm)
save("intros_char.json", ic)
