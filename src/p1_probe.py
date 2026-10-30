# -*- coding: utf-8 -*-
"""P1 侦察：统计章节脚本里的指令形状，为解析器定型。"""
import os, re, collections, json

RAW = r"D:\LegendOfMortal Wiki\data\raw"
CJK = re.compile(r"[\u4e00-\u9fff]")

pats = {
    "say_story": re.compile(r'say\(\s*luamanager\.GetStoryText\(\s*"([^"]+)"'),
    "say_other": re.compile(r'say\(\s*"([^"]*)"'),
    "setcharacter": re.compile(r'setcharacter\(\s*([^)]*)\)'),
    "setsaydialog": re.compile(r'setsaydialog\(\s*([^)]*)\)'),
    "setflag": re.compile(r'SetFlag\(\s*"([^"]+)"\s*,\s*([^)]*)\)'),
    "dice": re.compile(r'checkpointmanager\.Dice\(\s*"([^"]+)"'),
    "option": re.compile(r'"(O_[^"|]+)\|([^"]*)"'),
    "runblock": re.compile(r'runblock\(\s*([^)]*)\)'),
    "if_line": re.compile(r'^\s*(if|elseif)\s+(.+?)\s+then'),
}

def main():
    sc = os.path.join(RAW, "scripts")
    files = [f for f in os.listdir(sc) if f.endswith(".txt")]
    hits = collections.Counter()
    shapes = collections.Counter()
    chars = 0
    chars_per_file = []
    for fn in files:
        s = open(os.path.join(sc, fn), encoding="utf-8").read()
        chars += len(CJK.findall(s))
        if "GetStoryText" not in s:
            continue
        chars_per_file.append((len(CJK.findall(s)), fn))
        for name, rx in pats.items():
            hits[name] += len(rx.findall(s))
        for line in s.splitlines():
            t = line.strip()
            if "GetStoryText" in t or t.startswith("say("):
                shapes[re.sub(r'"[^"]*"', '"…"', t)[:70]] += 1
            elif t.startswith(("setcharacter", "setsaydialog")):
                shapes[re.sub(r'"[^"]*"', '"…"', t)[:70]] += 1

    chars_per_file.sort(reverse=True)
    print("script files:", len(files), "with GetStoryText:", len(chars_per_file))
    print("cjk:", chars)
    print("hits:", dict(hits))
    print("\n--- line shapes top 18 ---")
    for k, v in shapes.most_common(18):
        print(f"{v:6d}  {k}")
    print("\n--- biggest 5 scripts ---")
    for c, fn in chars_per_file[:5]:
        print(f"{c:7d}  {fn}")
    # 每个 say 对应几个 key
    keys = set()
    for fn in files:
        s = open(os.path.join(sc, fn), encoding="utf-8").read()
        keys.update(pats["say_story"].findall(s))
    print("\ndistinct story keys referenced:", len(keys))

if __name__ == "__main__":
    main()
