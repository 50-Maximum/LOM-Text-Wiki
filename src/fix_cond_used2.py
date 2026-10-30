# -*- coding: utf-8 -*-
"""直接用行定位修好条件反查：加载 cond_used.json 并作为初始反查表。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
lines = open(P, encoding="utf-8").read().split("\n")

# 1) 找 COND_LIB 块结束位置
idx = None
for i, ln in enumerate(lines):
    if ln.startswith("COND_LIB = {}"):
        idx = i
        break
if idx is None:
    print("找不到 COND_LIB"); raise SystemExit(1)
end = idx
for j in range(idx, idx + 12):
    if lines[j].startswith("except Exception:"):
        end = j + 2
        break
if "COND_USED" not in "\n".join(lines[idx:end + 6]):
    lines[end:end] = [
        "",
        "COND_USED = {}",
        "try:",
        '    _cup = os.path.join(BASE, "data", "cond_used.json")',
        "    if os.path.exists(_cup):",
        "        COND_USED = json.load(open(_cup, encoding=\"utf-8\"))",
        "except Exception:",
        "    COND_USED = {}",
    ]
    print("已插入 COND_USED 加载")

# 2) 初始反查表
for i, ln in enumerate(lines):
    if ln.strip() == "_COND_USED = {}":
        lines[i] = "_COND_USED = {k: set(v) for k, v in COND_USED.items()}"
        print("反查表已并入 cond_used.json（第 %d 行）" % (i + 1))
        break

open(P, "w", encoding="utf-8").write("\n".join(lines))
py_compile.compile(P, doraise=True)
print("syntax ok")
