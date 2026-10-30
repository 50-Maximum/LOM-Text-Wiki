# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for pre in ["崆峒·", "岭南派·", "巫灵教·"]:
    print("==", pre)
    for r in c.execute("select name from pages where type='人物' and name like ?", (pre + "%",)):
        print("   ", r["name"])
cp = json.load(open(r"D:\LegendOfMortal Wiki\data\chars_prefix.json", encoding="utf-8"))
print("\nchars_prefix 里含崆峒/岭南 的：")
for k, v in cp.items():
    if "崆峒" in str(v) or "岭南" in str(v):
        print("   ", k, "→", v)
