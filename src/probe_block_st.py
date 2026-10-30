# -*- coding: utf-8 -*-
import io, sys, sqlite3, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
st = {}
for sc, ev in c.execute("select script,event from scene_time"):
    st.setdefault(ev, []).append(sc)
blocks = {}
for f in glob.glob(r"D:\LegendOfMortal Wiki\data\guide\*.txt"):
    t = open(f, encoding="utf-8", errors="replace").read()
    for b in t.split("####"):
        b = b.strip().lstrip("| ")
        if "触发条件" not in b or "事件内容" not in b:
            continue
        m = re.search(r"第[一二三四]年", b)
        name = re.sub(r"\s+", "", b[:m.start()] if m else "")[:30]
        if not name:
            continue
        i, j = b.find("触发条件"), b.find("事件内容")
        cond = re.sub(r"\s+", "", b[i + 4: j])
        if name not in blocks or len(cond) > len(blocks[name]):
            blocks[name] = cond
print("攻略块唯一名:", len(blocks), " scene_time 事件名:", len(st))
same = [n for n in blocks if n in st]
print("同名可直接挂到脚本:", len(same))
for n in same[:15]:
    print("   ", n, "->", st[n][:3], "|", blocks[n][:50])
