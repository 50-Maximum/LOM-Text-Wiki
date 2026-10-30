# -*- coding: utf-8 -*-
"""解析剧本里所有 choose() 菜单：每个选项的文案、解锁条件、选中后的效果与去向。

写法（三种以上，统一处理）：
    local talk = {} / local door = {} / local option_001 = {}
    talk[1]  = "talk+O_6_6_2_Break_01_001+0+0"
    talk[11] = Ch_6_6_2_Break_01_008 and "event+O_6_6_2_Break_01_014+0+0" or "~x"
    door[8]  = S0604_01 and "event+O_Door_001_007+0+0" or "~x"
    local choice_talk = choose(talk)
    if choice_talk == 11 then
        --index:O_6_6_2_Break_01_014
        statmodifymanager.SetFlag("Talk_Option_02", 1)
        luamanager.SetNextScript("ch6_7_1")

输出：data/talk_menus.json（剧本 → 菜单块）、data/optkey_text.json（O_键 → 文案）
"""
import io, sys, os, re, json, gzip, glob, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(B, "data", "raw", "scripts")

TXT = {}
_p = os.path.join(B, "data", "build", "text.json")
if os.path.exists(_p):
    TXT = json.load(open(_p, encoding="utf-8"))

COND, SWITCH = {}, {}
try:
    d = json.loads(gzip.open(os.path.join(B, "data", "mod_res", "LOMAssistant.conditions.json.gz"),
                             "rb").read().decode("utf-8"))
    COND = d.get("Conditions") or {}
    SWITCH = d.get("Switches") or {}
except Exception as e:
    print("判定库读取失败:", e)


def cond_text(cid):
    if not cid:
        return ""
    v = COND.get(cid)
    if isinstance(v, str) and v.strip():
        return v.strip()
    arr = SWITCH.get(cid)
    if isinstance(arr, list) and arr:
        if len(arr) == 1:
            return str(arr[0]).strip()
        return "（%d 种情形之一）%s" % (len(arr), "；".join(str(x) for x in arr[:3]))
    return ""


RE_DECL = re.compile(r"^\s*local\s+(\w+)\s*=\s*\{\s*\}\s*$")
RE_SET = re.compile(r"^\s*(\w+)\s*\[\s*(\d+)\s*\]\s*=\s*(.+?)\s*$")
RE_CHOOSE = re.compile(r"^\s*local\s+(\w+)\s*=\s*choose\(\s*(\w+)\s*\)")
RE_KEY = re.compile(r"[\"'](?:[A-Za-z]+\+)?(O_[A-Za-z0-9_]+)\+")
RE_KEY_PLAIN = re.compile(r"^[\"'](O_[A-Za-z0-9_]+)[\"']\s*$")
RE_COND = re.compile(r"^([A-Za-z_]\w*)\s+and\s+")
RE_BRANCH = re.compile(r"^\s*(?:if|elseif)\s+(\w+)\s*==\s*(\d+)\s+then\s*$")
RE_INDEX = re.compile(r"--index:\s*(O_[A-Za-z0-9_]+)")
RE_JUMP = re.compile(r'(?:SetNextScript|ChangeScene)\(\s*"([^"]+)"')
RE_SETFLAG = re.compile(r'SetFlag\(\s*"([^"]+)"\s*,\s*(-?\d+)\s*\)')
RE_ADDFLAG = re.compile(r'AddFlag\(\s*"([^"]+)"\s*,\s*(-?\d+)\s*\)')

MENU_LABEL = {"talk": "对话菜单", "door": "门事件菜单", "move": "移动菜单"}


def _ind(s):
    return len(s) - len(s.lstrip("\t"))


out = {}
optkey_text = {}
stat = collections.Counter()

for f in sorted(glob.glob(os.path.join(RAW, "*.txt"))):
    script = os.path.basename(f)[:-4]
    try:
        lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
    except Exception:
        continue

    # 1) 所有菜单表声明 + choose() 变量映射
    decl, choosemap = {}, {}
    for i, ln in enumerate(lines):
        m = RE_DECL.match(ln)
        if m:
            decl.setdefault(m.group(1), i)
        cm = RE_CHOOSE.match(ln)
        if cm:
            choosemap[cm.group(1)] = cm.group(2)
    used = set(choosemap.values())          # 只保留真的被 choose() 使用的表
    if not used:
        continue

    menus = {v: {"pos": decl.get(v, 0), "options": {}} for v in used}

    # 2) 选项赋值
    for ln in lines:
        m = RE_SET.match(ln)
        if not m:
            continue
        var, idx, rhs = m.group(1), int(m.group(2)), m.group(3)
        if var not in menus:
            continue
        km = RE_KEY.search(rhs) or RE_KEY_PLAIN.match(rhs)
        if not km:
            continue
        key = km.group(1)
        cm = RE_COND.match(rhs)
        cid = cm.group(1) if (cm and not cm.group(1).startswith("choice_")) else ""
        menus[var]["options"][idx] = {"idx": idx, "key": key, "text": TXT.get(key, ""),
                                      "cond_id": cid, "cond": cond_text(cid),
                                      "next": "", "terminal": 0, "effects": []}
        stat["选项"] += 1
        if cid:
            stat["带条件"] += 1

    # 3) 用 --index: 标记切分支体，取效果与去向
    marks = [(i, RE_INDEX.search(l).group(1)) for i, l in enumerate(lines) if RE_INDEX.search(l)]
    for n, (li, key) in enumerate(marks):
        nxt = marks[n + 1][0] if n + 1 < len(marks) else len(lines)
        lim = _ind(lines[li])
        end = nxt - 1
        for k in range(li + 1, min(nxt, len(lines))):
            if lines[k].strip() == "end" and _ind(lines[k]) <= lim:
                end = k
                break
        idx_hint = var_hint = None
        for k in range(li - 1, max(-1, li - 9), -1):
            bm = RE_BRANCH.match(lines[k])
            if bm:
                var_hint, idx_hint = bm.group(1), int(bm.group(2))
                break
        if idx_hint is None:
            continue
        mv = choosemap.get(var_hint, var_hint)
        menu = menus.get(mv)
        if not menu:
            continue
        o = menu["options"].get(idx_hint)
        if o is None:
            o = menu["options"][idx_hint] = {"idx": idx_hint, "key": key,
                                             "text": TXT.get(key, ""), "cond_id": "", "cond": "",
                                             "next": "", "terminal": 0, "effects": []}
        if o.get("key") != key:
            o["key"] = key
            o["text"] = TXT.get(key, o.get("text") or "")
        fx = []
        for k in range(li, end + 1):
            ln2 = lines[k]
            for fm in RE_SETFLAG.finditer(ln2):
                fx.append("旗标%s＝%s" % (fm.group(1), fm.group(2)))
            for fm in RE_ADDFLAG.finditer(ln2):
                fx.append("旗标%s%+d" % (fm.group(1), int(fm.group(2))))
            if not o["next"]:
                jm = RE_JUMP.search(ln2)
                if jm:
                    o["next"] = jm.group(1)
                    o["terminal"] = 1 if jm.group(1) in ("Title", "Combat") else 0
        seen = []
        for x in fx:
            if x not in seen:
                seen.append(x)
        o["effects"] = seen

    blocks = []
    for var, menu in menus.items():
        opts = [o for o in menu["options"].values() if o.get("key")]
        if not opts:
            continue
        opts.sort(key=lambda x: x["idx"])
        blocks.append({"var": var, "label": MENU_LABEL.get(var, "菜单"),
                       "pos": menu["pos"], "options": opts})
        stat["菜单"] += 1
    if blocks:
        out[script] = blocks

for k, v in TXT.items():
    if k.startswith("O_"):
        optkey_text[k] = v

json.dump(out, open(os.path.join(B, "data", "talk_menus.json"), "w", encoding="utf-8"),
          ensure_ascii=False)
json.dump(optkey_text, open(os.path.join(B, "data", "optkey_text.json"), "w", encoding="utf-8"),
          ensure_ascii=False)

print("剧本 %d 个 → 有菜单 %d 个" % (len(glob.glob(os.path.join(RAW, "*.txt"))), len(out)))
print("菜单块 %d，选项 %d（带解锁条件 %d）" % (stat["菜单"], stat["选项"], stat["带条件"]))
print("O_ 键文案 %d 条" % len(optkey_text))

for sc, key in (("ch6_6_2_break_start_01", "014"), ("door_001_01", "007")):
    print("\n=== 抽查", sc)
    for b in out.get(sc, []):
        for o in b["options"]:
            if o["key"].endswith(key):
                print("  [%s] %-22s 条件=%s 效果=%s 去向=%s" %
                      (b["var"], o["text"], o["cond"] or "无", "、".join(o["effects"]) or "无",
                       o["next"] or "-"))
