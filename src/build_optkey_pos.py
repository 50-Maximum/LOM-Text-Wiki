# -*- coding: utf-8 -*-
"""选项键 → 它出现在哪个剧本的第几句（「选择「X」后进入」要直接跳到那一场）。

三个来源：
  1) choices.options（choose(option_xxx) 类）
  2) branch_nodes 里 kind=choose 且 text 就是 O_ 键的行（talk/door 类）
  3) talk_menus.json 里记录的菜单所在剧本（兜底，seq=0）
"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

pos = {}

# 1) choices 表
for script, seq, opts in c.execute("select script,seq,options from choices"):
    try:
        arr = json.loads(opts or "[]")
    except Exception:
        continue
    for o in arr:
        k = (o.get("key") or "").strip()
        if k and k not in pos:
            pos[k] = {"script": script, "seq": seq, "src": "choices"}

# 2) branch_nodes 里直接写 key 的
for script, seq, text in c.execute("""select script,seq,text from branch_nodes
                                      where kind='choose' and text like 'O\\_%' escape '\\'"""):
    k = (text or "").strip()
    if k.startswith("O_") and k not in pos:
        pos[k] = {"script": script, "seq": seq, "src": "branch_nodes"}

# 3) talk_menus 兜底
try:
    TM = json.load(open(B + r"\data\talk_menus.json", encoding="utf-8"))
    for script, blks in TM.items():
        for b in blks:
            for o in b.get("options") or []:
                k = o.get("key") or ""
                if k and k not in pos:
                    pos[k] = {"script": script, "seq": 0, "src": "talk_menus"}
except Exception as e:
    print("talk_menus 读取失败", e)

json.dump(pos, open(B + r"\data\optkey_pos.json", "w", encoding="utf-8"), ensure_ascii=False)
print("选项位置 %d 条" % len(pos))
for k in ("O_6_6_2_Break_01_014", "O_Door_001_007", "O_5_6_5_3_002"):
    print("  ", k, "→", pos.get(k))

try:
    txt = json.load(open(B + r"\data\optkey_text.json", encoding="utf-8"))
    miss = [k for k in txt if k not in pos]
    print("\n有文案但定位不到：%d / %d" % (len(miss), len(txt)))
    print("  例：", miss[:6])
except Exception:
    pass
