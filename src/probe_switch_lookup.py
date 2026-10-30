# -*- coding: utf-8 -*-
import io, sys, gzip, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lib = json.loads(gzip.open(r"D:\LegendOfMortal Wiki\data\mod_res\LOMAssistant.conditions.json.gz", "rb").read().decode("utf-8"))
SW, CD = lib["Switches"], lib["Conditions"]
for k in ("Ch_6_2_1_003", "Ch_6_2_2_Break_01_002", "Ch_5_6_2_2_001", "S0003_01_001"):
    print(k, "->", SW.get(k) or CD.get(k))
print("\nSwitches 里 Ch_ 开头条数:", sum(1 for k in SW if k.startswith("Ch_")))
print("样例:", [k for k in SW if k.startswith("Ch_")][:6])
