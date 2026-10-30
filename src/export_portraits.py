# -*- coding: utf-8 -*-
"""提取人物立绘：speaker_id → portrait_* bundle → web/portrait/<id>.png，
并生成 slug → 图片 的 web/portraits.json。"""
import io, os, re, sys, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

BASE = r"D:\LegendOfMortal Wiki"
BUNDLES = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\StreamingAssets\aa\StandaloneWindows64"
OUT = os.path.join(BASE, "web", "portrait")
os.makedirs(OUT, exist_ok=True)

# 1. bundle 名清单 → 归一化键
bundle_of = {}
for f in os.listdir(BUNDLES):
    if not f.startswith("portrait_") or "_assets_all" not in f:
        continue
    base = f.split("_assets_all")[0]          # portrait_girl_05
    key = base[len("portrait_"):]             # girl_05
    for k in {key, key.replace("_", ""), key.upper(), key.replace("_0", "_")}:
        bundle_of[k.lower()] = f
print("portrait bundle 数", len(bundle_of))

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
rows = con.execute("""select speaker_id, speaker, count(*) n from lines
                      where speaker_id<>'' group by speaker_id, speaker
                      order by n desc""").fetchall()

# 别名表：名字 → slug
alias = {}
for r in con.execute("select alias, slug from aliases"):
    alias[r["alias"]] = r["slug"]
for r in con.execute("select name, slug from pages where type='人物'"):
    alias.setdefault(r["name"], r["slug"])
    alias.setdefault(r["name"].split("·")[-1], r["slug"])


def find_bundle(sid):
    s = sid.lower()
    cands = [s, s.replace("_", "")]
    m = re.fullmatch(r"([a-z_]+?)(\d+)(?:_\d+)?", s)
    if m:
        pre, num = m.group(1), m.group(2)
        cands += ["%s_%s" % (pre, num),
                  "%s_%02d" % (pre, int(num)) if len(num) <= 2 else "%s_%03d" % (pre, int(num)),
                  "%s_%03d" % (pre, int(num)),
                  "%s_%04d" % (pre, int(num)),
                  "%s%d" % (pre, int(num))]
    for c in cands:
        if c in bundle_of:
            return bundle_of[c]
    # 退化：去掉编号后若存在同名 bundle，就用它（sister1 → sister）
    stem = re.sub(r"[_\d]+$", "", s)
    if stem and stem in bundle_of:
        return bundle_of[stem]
    return None


done, miss, noport = [], [], []
for r in rows:
    sid = r["speaker_id"]
    if sid in ("player",) and False:
        continue
    b = find_bundle(sid)
    if not b:
        miss.append(sid)
        continue
    out_p = os.path.join(OUT, "%s.png" % sid)
    if os.path.exists(out_p):
        done.append(sid)
        continue
    try:
        env = UnityPy.load(os.path.join(BUNDLES, b))
    except Exception as e:
        miss.append(sid)
        continue
    sprites = {}
    for o in env.objects:
        if o.type.name != "Sprite":
            continue
        try:
            d = o.read()
            nm = d.m_Name
        except Exception:
            continue
        sprites.setdefault(nm, o)
    if not sprites:
        noport.append(sid)
        continue
    pick = None
    for pref in ("normal", "fine", "default", "calm"):
        if pref in sprites:
            pick = sprites[pref]
            break
    if pick is None:
        pick = list(sprites.values())[0]
    try:
        img = pick.read().image
    except Exception:
        noport.append(sid)
        continue
    if img is None:
        noport.append(sid)
        continue
    if img.height > 900:
        img = img.resize((int(img.width * 900 / img.height), 900))
    img.save(out_p)
    done.append(sid)

print("导出 %d 张；无 bundle %d；无图 %d" % (len(done), len(miss), len(noport)))
print("无 bundle 的 id:", miss[:30])
print("有 bundle 无图:", noport[:20])

# 4. slug → 图
mapping, nomatch = {}, []
for r in rows:
    sid, spk = r["speaker_id"], r["speaker"]
    if sid not in done:
        continue
    slug = alias.get(spk) or alias.get((spk or "").split("·")[-1])
    if not slug:
        nomatch.append((sid, spk))
        continue
    mapping.setdefault(slug, "portrait/%s.png" % sid)

json.dump(mapping, open(os.path.join(BASE, "web", "portraits.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
print("slug→立绘 %d 条；说话人对不上条目 %d 例：%s"
      % (len(mapping), len(nomatch), nomatch[:12]))
