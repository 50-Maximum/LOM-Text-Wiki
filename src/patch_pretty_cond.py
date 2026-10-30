# -*- coding: utf-8 -*-
"""条件链展开成人话：条件 ID｜…  →  判定 ID（可读条件）；链用「且」连接。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

if "def pretty_cond" not in s:
    anchor = "CH_ORDER = {\"序章\": 0, \"第0章\": 1, \"第1章\": 2}"
    assert anchor in s
    helper = '''def pretty_cond(t):
    """把「条件 X｜需=1 > 条件 Y｜需<10」展开成一句能读的话。"""
    if not t:
        return t
    def _rep(m):
        cid = m.group(1)
        info = COND_LIB.get(cid) or {}
        attrs = [a for a in (info.get("attrs") or []) if a]
        if attrs:
            shown = "／".join(attrs[:5])
            if len(attrs) > 5:
                shown += " 等 %d 条" % len(attrs)
            return "判定 %s（%s）" % (cid, shown)
        return "判定 %s" % cid
    t = re.sub(r"条件\\s+([A-Za-z][A-Za-z0-9_]{2,})\\s*｜[^>]*", _rep, t)
    t = t.replace(" > ", " 且 ")
    return t.strip()


'''
    s = s.replace(anchor, helper + anchor, 1)

old = '''        choices.append({"seq": seq, "kind": kind, "idx": idx, "text": text,
                        "cond": cond, "flags": json.loads(fl or "[]"),'''
new = '''        choices.append({"seq": seq, "kind": kind, "idx": idx, "text": text,
                        "cond": pretty_cond(cond), "flags": json.loads(fl or "[]"),'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("pretty_cond 已接入")
