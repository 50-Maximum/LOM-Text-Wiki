# -*- coding: utf-8 -*-
import io, sys, gzip, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lib = json.loads(gzip.open(r"D:\LegendOfMortal Wiki\data\mod_res\LOMAssistant.conditions.json.gz", "rb").read().decode("utf-8"))
SW = lib["Switches"]
for k in ("S0003_01_02_001", "Ch_0_M_03_02_01_001", "Ch_1_5_1_1"):
    print("\n", k, "->", SW.get(k) if k in SW else "（不在库）")
# 库里多值比例
multi = sum(1 for v in SW.values() if isinstance(v, list) and len(v) > 1)
print("\n多值条目:", multi, "/", len(SW))
# 与 branch_nodes 对照
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("\nbranch_nodes 骰子行样例:")
for r in c.execute("select script,seq,idx,text,cond from branch_nodes where kind='dice' and script='S0003_01_02' order by idx limit 6"):
    print("  ", r)
