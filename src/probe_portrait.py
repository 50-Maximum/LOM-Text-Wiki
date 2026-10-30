# -*- coding: utf-8 -*-
"""摸清立绘/物品图的命名：读 Addressables catalog，再看几个 bundle 里的资源名。"""
import io, os, sys, json, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\StreamingAssets\aa"
BUNDLES = os.path.join(ROOT, "StandaloneWindows64")

cat = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
print("catalog keys:", list(cat.keys())[:10])
for k, v in cat.items():
    if isinstance(v, list):
        print("  %s: list %d" % (k, len(v)))
    elif isinstance(v, dict):
        print("  %s: dict %d" % (k, len(v)))

# 找条目里的内部 id / 地址
for k in ("m_InternalIds", "m_ProviderIds", "m_BucketDataString", "m_KeyDataString"):
    if k in cat:
        v = cat[k]
        print("\n%s sample:" % k, str(v)[:300])

# 直接看 bundle 内资源名
for b in ("portrait_tangmen_assets_all_569784352f72dda0607767bacd20b744.bundle",
          "portrait_girl_05_assets_all_4e534e78891ef8c95d61bc72a47b99df.bundle",
          "picture_assets_all_b3d1a6f0e9d7d9df41e76ce75acff0c7.bundle"):
    p = os.path.join(BUNDLES, b)
    if not os.path.exists(p):
        print("missing", b)
        continue
    env = UnityPy.load(p)
    cnt = collections.Counter()
    names = []
    for o in env.objects:
        cnt[o.type.name] += 1
        if o.type.name in ("Sprite", "Texture2D", "TextAsset"):
            try:
                nm = o.read(check_read=False).m_Name
            except Exception:
                nm = "?"
            names.append((o.type.name, nm))
    print("\n== %s" % b.split("_assets_all")[0])
    print("   类型:", dict(cnt))
    print("   名字前 30:", [n for _, n in names[:30]])
