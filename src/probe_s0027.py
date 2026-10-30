# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== S0027_01 外姓/拜师")
for sc, seq, sp, tx in c.execute("""select script,seq,speaker,text from lines where script='S0027_01'
        and (text like '%外姓%' or text like '%拜师%') order by seq limit 8"""):
    print("  %-4s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:90]))
d = json.load(open(r"D:\LegendOfMortal Wiki\data\intros_char.json", encoding="utf-8"))
for f in d["人物/唐中翎"]["footnotes"]:
    if f.get("script") == "S0027_01":
        print("\n旧脚注6:", f.get("quote"))
