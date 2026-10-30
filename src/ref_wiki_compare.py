# -*- coding: utf-8 -*-
"""参考 wiki（简中）与我们页面比对：缺人、门派不符、年表事件没对上。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
ref = json.load(open(B + r"\ref_wiki\characters.json", encoding="utf-8"))
tl = json.load(open(B + r"\ref_wiki\timeline.json", encoding="utf-8"))
c = sqlite3.connect(B + r"\wiki.db").cursor()

ours = {}
for nm, slug, hidden in c.execute("select name,slug,hidden from pages where type='人物'"):
    bare = nm.split("·")[-1]
    pre = nm.split("·")[0] if "·" in nm else ""
    ours[bare] = (pre, slug, hidden)
alias = {a: s for a, s in c.execute("select alias,slug from aliases")}

missing, diff = [], []
for ch in ref:
    nm = ch["name"] or ch["title"]
    if not nm or nm in ("？？？", "无名"):
        continue
    pre = (ch["tags"][1] if len(ch["tags"]) > 1 else "")
    if nm in ours:
        op = ours[nm][0]
        if pre and op and pre != op:
            diff.append((nm, op, pre))
    elif nm in alias:
        pass
    else:
        missing.append((nm, pre, ch["chtitle"], ch["key"]))

print("参考人物 %d；我们缺 %d 个；门派不符 %d 个" % (len(ref), len(missing), len(diff)))
print("\n=== 缺的人物（参考里有、我们没有）")
out = ["%s(%s%s)" % (n, p, ("/"+t) if t else "") for n, p, t, k in missing]
for i in range(0, len(out), 5):
    print("  " + "  ".join(out[i:i + 5]))
print("\n=== 门派不符（我们 / 参考）")
for n, a, b in diff[:40]:
    print("  %-8s %-8s → %s" % (n, a or "—", b))

print("\n=== 年表事件对应")
evnames = [r[0] for r in c.execute("select name from pages where type='事件'")]
for r in tl:
    e = r["event"].strip()
    hit = [x for x in evnames if x == e] or [x for x in evnames if e and (e in x or x in e)]
    print("  [%s] %-22s %s%s%s → %s" % (r["kind"], e[:22], r["year"], r["month"], r["xun"],
                                        (hit[0] if hit else "未对上")))
