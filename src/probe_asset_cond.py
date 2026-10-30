# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, path + "[%d]" % i)
    elif isinstance(obj, str):
        yield path, obj


for n in ["cond_lib.json", "scene_conds.json"]:
    p = os.path.join(B, n)
    d = json.load(open(p, encoding="utf-8"))
    print("==", n)
    cnt = 0
    for path, s in walk(d):
        if "资产" in s or "负债" in s:
            print("   %-60s %s" % (path[:60], s[:120]))
            cnt += 1
            if cnt >= 10:
                break
    print("   命中", cnt)
