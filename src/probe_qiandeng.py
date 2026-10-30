# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
fx = json.load(open(B + r"\factions_fix.json", encoding="utf-8"))
par = fx.get("parent", {})
print("千灯楼 上级:", par.get("千灯楼", "（顶层）"))
print("千灯楼 是否被删:", "千灯楼" in set(fx.get("delete", [])))
print("千灯楼 有导语:", "千灯楼" in (fx.get("intro", {}) or {}))
c = sqlite3.connect(B + r"\wiki.db").cursor()
print("\n千灯楼 成员（char_faction）:")
for r in c.execute("""select n.name, cf.faction from char_faction cf
                      join names n on n.id=cf.char_id where cf.faction='千灯楼'"""):
    print("   ", r[0])
print("\n千灯楼 作为势力页的提及数:",
      c.execute("select mentions from pages where slug='势力/千灯楼'").fetchone())
print("千灯楼 是否在 place_children:",
      c.execute("select count(*) from place_children where slug='势力/千灯楼'").fetchone())
