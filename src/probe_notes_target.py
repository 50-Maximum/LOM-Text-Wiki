# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for sc in ["S8400_01", "S8400_01_01", "travel_result_401_501", "travel_result_401_504",
           "S9903_01", "ch0_5", "meeting_option_705_01"]:
    print("==", sc)
    for r in c.execute("select type,name,note from notes where script=?", (sc,)):
        print("   [%s] %s :: %s" % (r["type"], r["name"], (r["note"] or "")[:110]))
