# -*- coding: utf-8 -*-
"""全库审计：原始 Lua 里是否有「条件选项」——即某个选项只在 if 分支里才被加进菜单。
判定方法：在 local option_X = {} 到 choose(option_X) 之间维护嵌套深度，
任何 option_X[n] = "..." 出现在深度>0 处，即为条件选项。
"""
import io, sys, os, re, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"

RE_DECL = re.compile(r"^\s*local\s+(option_\w+)\s*=\s*\{\s*\}")
RE_SET = re.compile(r"^\s*(option_\w+)\s*\[\s*(\d+)\s*\]\s*=\s*[\"']([^\"']+)[\"']")
RE_CHOOSE = re.compile(r"\bchoose\s*\(\s*(option_\w+)\s*[,)]")
RE_OPEN = re.compile(r"^\s*(if\b.*\bthen\s*$|for\b.*\bdo\s*$|while\b.*\bdo\s*$|function\b|do\s*$)")
RE_END = re.compile(r"^\s*end\s*$")

files = sorted(glob.glob(os.path.join(RAW, "*.txt")))
print("扫描 %d 个剧本" % len(files))

cond_opts = []      # (script, var, idx, key, cond_hint)
total_blocks = 0
total_opts = 0

for f in files:
    script = os.path.basename(f)[:-4]
    try:
        lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
    except Exception:
        continue
    i = 0
    while i < len(lines):
        m = RE_DECL.match(lines[i])
        if not m:
            i += 1
            continue
        var = m.group(1)
        total_blocks += 1
        depth = 0
        stack = []          # 进入深度时的 if 头文字
        j = i + 1
        while j < len(lines) and j < i + 4000:
            ln = lines[j]
            if RE_CHOOSE.search(ln) and var in ln:
                break
            if RE_OPEN.match(ln):
                depth += 1
                stack.append(ln.strip()[:70])
            elif RE_END.match(ln):
                depth = max(0, depth - 1)
                if stack:
                    stack.pop()
            else:
                ms = RE_SET.match(ln)
                if ms and ms.group(1) == var:
                    total_opts += 1
                    if depth > 0:
                        cond_opts.append({
                            "script": script, "var": var,
                            "idx": int(ms.group(2)), "key": ms.group(3),
                            "cond": " / ".join(stack[-2:])})
            j += 1
        i = max(j, i + 1)

print("选项块 %d 个，选项 %d 条" % (total_blocks, total_opts))
print("条件选项（在 if/for 内加入菜单）%d 条，涉及剧本 %d 个"
      % (len(cond_opts), len({x['script'] for x in cond_opts})))

json.dump(cond_opts, open(r"D:\LegendOfMortal Wiki\data\cond_options.json", "w",
                          encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n=== 前 15 条样例")
for x in cond_opts[:15]:
    print("  %-22s %-14s [%s] %s" % (x["script"], x["var"], x["idx"], x["key"]))
    print("        条件印记:", x["cond"])
