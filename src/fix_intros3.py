# -*- coding: utf-8 -*-
"""修导语 dict 形式：人物/百万赵活、人物/裴红腊；并清掉多余的字符串键。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(p, encoding="utf-8"))

new_zhao = ("百万赵活是梦境里的小竹所造的机关人。触发鹦鹉事件之后，梦中的鹦鹉会驾驶这具机关人出战，"
            "郁竹在梦里喊「出击，百万赵活」。")
node = d.get("人物/百万赵活")
if isinstance(node, dict):
    node["text"] = new_zhao
    print("已改 人物/百万赵活 →", node["text"][:50])
d.pop("百万赵活", None)

node = d.get("人物/裴红腊")
if isinstance(node, dict):
    old = node.get("text") or ""
    node["text"] = old.replace("崆峒派", "青城派")
    print("裴红腊：", old[:40], "→", node["text"][:50])

json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("写回完成")
