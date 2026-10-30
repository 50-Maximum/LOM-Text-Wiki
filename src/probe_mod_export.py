# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\LOMAssistant.dll"
raw = open(p, "rb").read()
asc = [s.decode("ascii", "ignore") for s in re.findall(rb"[\x20-\x7e]{4,}", raw)]
print("== 含 Export / Dump / Save / File 的字符串 ==")
for s in asc:
    if re.search(r"(Export|Dump|WriteAll|\.json|\.csv|\.txt)", s):
        print("   ", s[:120])
print("\n== UTF-16 中文串（含 导出/事件/触发/条件）==")
u = raw.decode("utf-16-le", errors="ignore")
u = re.sub(r"[\x00-\x08\x0b-\x1f]", "\n", u)
seen = set()
for m in re.finditer(r"[^\n]{0,60}(导出|事件|触发|条件|要求)[^\n]{0,80}", u):
    s = m.group(0).strip()
    if s and s not in seen and len(s) > 3:
        seen.add(s)
        print("   ", s[:130])
    if len(seen) > 45:
        break
