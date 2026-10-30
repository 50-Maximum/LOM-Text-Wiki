# -*- coding: utf-8 -*-
import io, sys, os, re, glob, gzip, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lib = json.loads(gzip.open(r"D:\LegendOfMortal Wiki\data\mod_res\LOMAssistant.conditions.json.gz", "rb").read().decode("utf-8"))
SW, CD = lib["Switches"], lib["Conditions"]
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
pos, story = set(), set()
for f in glob.glob(os.path.join(base, "*.txt")):
    t = open(f, encoding="utf-8", errors="replace").read()
    pos.update(re.findall(r'checkpointmanager\.Position\("([^"]+)"\)', t))
    story.update(re.findall(r'statmodifymanager\.AddStory\("([^"]+)"\)', t))
print("Position 编号:", len(pos), " 在库里:", sum(1 for x in pos if x in SW or x in CD))
for x in list(pos)[:6]:
    print("   ", x, "->", SW.get(x) or CD.get(x))
print("\nAddStory 编号:", len(story), " 在库里:", sum(1 for x in story if x in SW or x in CD))
for x in list(story)[:6]:
    print("   ", x, "->", SW.get(x) or CD.get(x))
# 库里 key 前缀分布（看有没有 scene/position 类）
pref = collections.Counter(re.sub(r"[\d_].*$", "", k) for k in SW)
print("\nSwitches 前缀 top:", pref.most_common(12))
