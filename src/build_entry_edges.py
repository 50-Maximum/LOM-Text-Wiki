# -*- coding: utf-8 -*-
"""从脚本控制流里抽出「谁在什么条件下跳进这个场景」，并把判定编号译成可读要求。

数据来源：
  剧本 *txt 的 checkpointmanager.Switch/Condition("编号")
  咖啡伴侣内置判定库 LOMAssistant.conditions.json.gz → 编号的可读要求（S0003_01_004 -> 道德 需<=40）
  选项文本取 branch_nodes(kind='choose', script, idx)
输出 data/entry_edges.json：{目标脚本: [{kind, src, src_title, text}]}
"""
import io, sys, os, re, glob, gzip, json, sqlite3, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
SCRIPTS = os.path.join(WIKI, "data", "raw", "scripts")
LIB = os.path.join(WIKI, "data", "mod_res", "LOMAssistant.conditions.json.gz")
OUT = os.path.join(WIKI, "data", "entry_edges.json")

lib = json.loads(gzip.open(LIB, "rb").read().decode("utf-8"))
SW, CD = lib["Switches"], lib["Conditions"]
c = sqlite3.connect(os.path.join(WIKI, "data", "wiki.db")).cursor()
TITLE = {s: t for s, t in c.execute("select script,title from scenes")}
CHOICE = {}
for sc, idx, tx in c.execute("select script,idx,text from branch_nodes where kind='choose'"):
    if tx:
        CHOICE.setdefault((sc, idx), tx)

pAssign = re.compile(r'(?:local\s+)?(\w+)\s*=\s*checkpointmanager\.(Switch|Condition)\("([^"]+)"\)')
pIf = re.compile(r'^(if|elseif)\s+(.+?)\s+then\s*$')
# 四种跳转：SetNextScript / SetCurrentStoryScript / SetCurrentTravelScript / SetTempScript(n, X)
pJump = re.compile(r'(?:SetNextScript|SetCurrentStoryScript|SetCurrentTravelScript|SetTempScript\(\s*\d+\s*,)\s*\(?\s*"([^"]+)"')
pEq = re.compile(r'^(\w+)\s*==\s*(\d+)$')


def pretty(cid):
    v = SW.get(cid) or CD.get(cid)
    if isinstance(v, list):
        v = "、".join(str(x) for x in v)
    if not v:
        return cid
    s = str(v).replace(" 需", "").replace("需>=", "≥").replace("需<=", "≤").replace("需=", "＝")
    s = s.replace(">=", "≥").replace("<=", "≤")
    return s


def main():
    edges = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(SCRIPTS, "*.txt"))):
        src = os.path.splitext(os.path.basename(f))[0]
        ls = open(f, encoding="utf-8", errors="replace").read().splitlines()
        var, stack = {}, []
        for ln in ls:
            s = ln.strip()
            if not s or s.startswith("--"):
                continue
            m = pAssign.search(s)
            if m:
                var[m.group(1)] = (m.group(2), m.group(3))
                continue
            m = pIf.match(s)
            if m:
                stack.append(m.group(2))
                continue
            if s == "end" or s.startswith("end ") or s == "end;":
                if stack:
                    stack.pop()
                continue
            m = pJump.search(s)
            if not m:
                continue
            cond = stack[-1] if stack else ""
            mq = pEq.match(cond)
            row = None
            if mq:
                vn, n = mq.group(1), int(mq.group(2))
                if vn in var:
                    k, cid = var[vn]
                    row = {"kind": "判定" if k == "Switch" else "条件", "text": pretty(cid)}
                elif vn.startswith("choice"):
                    tx = CHOICE.get((src, n))
                    row = {"kind": "选择", "text": tx or ("第%d个选项" % n)}
            if row is None:
                row = {"kind": "接续", "text": ""}
            if row:
                row["src"] = src
                row["src_title"] = TITLE.get(src) or src
                tgt = m.group(1)
                if row not in edges[tgt]:
                    edges[tgt].append(row)

    json.dump(edges, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    kinds = collections.Counter(r["kind"] for v in edges.values() for r in v)
    print("目标场景:", len(edges), " 边:", sum(len(v) for v in edges.values()), dict(kinds))
    for t in ("S0003_01_01", "S0003_01_03", "ch5_1_1", "ch0_5"):
        if t in edges:
            print("\n->", t, TITLE.get(t))
            for r in edges[t][:5]:
                print("    [%s] %s | %s" % (r["kind"], r["src_title"], r["text"][:60]))


if __name__ == "__main__":
    main()
