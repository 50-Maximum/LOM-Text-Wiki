# -*- coding: utf-8 -*-
"""重写画中仙；并入华仙儿/苏仙儿/唐仙儿别称。"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"

cf = BASE + r"\chars_fix.json"
c = json.load(open(cf, encoding="utf-8"))
c["merge"].update({"华仙儿": "画中仙", "苏仙儿": "画中仙", "唐仙儿": "画中仙"})
json.dump(c, open(cf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

fp = BASE + r"\intros_char.json"
d = json.load(open(fp, encoding="utf-8"))
d["人物/画中仙"] = {
 "text": "千灯楼第二代千面人魔，本名苏仙儿，又以「画中仙」华仙儿之名行走江湖（1）。她是虞小梅的亲姑姑，与她同姓虞（2），也是温夫人的亲生妹妹（3）。她曾在唐门以女弟子身份活动（4）。",
 "sections": [
  {"h": "分支", "html": "崆峒线：她现身搅局，助赵活救虞小梅，并以移魂大法宣告第四代千面人魔的最终饬令完成、尸心蛊失效（5）。<br>锦香宫线：温夫人死后，她受姊姊托付，以苏迎香、温夫人、锦香宫主的身份活下去（3）。"}
 ],
 "footnotes": [
  {"n": 1, "text": "画中仙自报：千灯楼第二代千面人魔苏仙儿", "script": "ch5_6_6_2", "quote": "千灯楼，第二代千面人魔，苏仙儿。"},
  {"n": 2, "text": "她向虞小梅承认自己是亲姑姑", "script": "ch6_7_5", "quote": "我不是你远亲的姑姑，我是你的亲姑姑，跟你一样姓虞。"},
  {"n": 3, "text": "温夫人逼亲生妹妹手刃姊姊、接替她的身份", "script": "ch6_7_5", "quote": "竟然逼亲生妹妹手刃姊姊。"},
  {"n": 4, "text": "她在唐门以师姐身份活动", "script": "ch6_4_3_4", "quote": "喊我师姐就好，你也是唐门女弟子。"},
  {"n": 5, "text": "她宣告第四代千面人魔最终饬令完成", "script": "ch5_6_7_3", "quote": "好，恭喜妳，第四代千面人魔的最终饬令，完成～！"}
 ]
}
json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("画中仙重写完成，别称已并入")
