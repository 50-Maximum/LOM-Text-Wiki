# -*- coding: utf-8 -*-
"""五零 05:20 修正：蝴蝶帮覆灭、孤云山派、养龙苑挂金国、华山派独立、毛二壮并入王二壮。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 1) 势力表：父子、合并、简介
ff = load("factions_fix.json")
par = ff.setdefault("parent", {})
mg = ff.setdefault("merge", {})
it = ff.setdefault("intro", {})

par["养龙苑"] = "金国"
par.pop("华山派", None)
mg["孤云山"] = "孤云山派"

it["势力/蝴蝶帮"] = {
    "text": "蝴蝶帮原本是江湖上一个门派，已被唐门剿灭。残党「蝴蝶双雄」怀恨在心，"
            "冒充唐门弟子潜伏下来，暗害了数名唐门弟子，又借一封假情书骗赵活夜里到后山。"
            "赵活揭破之后，对方自陈「从前是有的，就被你唐门多管闲事弄没啦」，"
            "又供出二人是朝廷下令缉捕的江洋大盗。",
    "footnotes": [
        {"n": 1, "text": "唐门弟子自陈蝴蝶帮已被唐门弄没。",
         "script": "S9905_01", "quote": "从前是有的，就被你唐门多管闲事弄没啦！"},
        {"n": 2, "text": "潜伏者承认自己是蝴蝶帮的人。",
         "script": "S9905_01", "quote": "谁是你师弟了？咱们是蝴蝶帮的人！"},
        {"n": 3, "text": "赵活点破二人身分是朝廷缉捕的江洋大盗。",
         "script": "S9905_01", "quote": "蝴蝶双雄，啊，你们是朝廷下令缉捕的江洋大盗吧！"},
    ],
}
save("factions_fix.json", ff)
print("势力表：养龙苑→金国；孤云山→孤云山派；蝴蝶帮简介已写；华山派移出全真派")

# 2) 华山派 独立（无上级）
ef = load("extra_factions.json")
if "华山派" in ef:
    ef["华山派"].pop("parent", None)
    save("extra_factions.json", ef)
    print("华山派：取消全真派上级")

# 3) 毛二壮 并入 王二壮
cf = load("chars_fix.json")
cf.setdefault("merge", {})["毛二壮"] = "王二壮"
save("chars_fix.json", cf)
print("并义 毛二壮 → 王二壮")

# 4) 王二壮 导语补备注
ic = load("intros_char.json")
node = ic.get("人物/王二壮")
if isinstance(node, dict):
    t = node.get("text") or ""
    if "毛二壮" not in t:
        node["text"] = t + "另一说，乞丐称本帮帮主名叫「毛二壮」，当是记错了自家帮主之名。"
        fn = node.setdefault("footnotes", [])
        fn.append({"n": len(fn) + 1, "text": "乞丐把帮主之名说成毛二壮。",
                   "script": "ch2_2_3_4_3_break_01_04_02",
                   "quote": "泥教畜生道法王，就是本帮帮主毛二壮！"})
        print("王二壮导语已加毛二壮备注")
save("intros_char.json", ic)
