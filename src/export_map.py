# -*- coding: utf-8 -*-
"""导出大地图：底图 web/map_bg.jpg + 节点坐标 web/map_nodes.json（标签自动避让，六道峡靠左）。"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

BASE = r"D:\LegendOfMortal Wiki"
SRC = os.path.join(BASE, "data", "art_dump", "Texture2D__background_map__sharedassets2_assets.png")
WEB = os.path.join(BASE, "web")

# level2 / Map 命名点：game 坐标（canvas 1920x1080，中心原点）
NAMED = [
    ("Home", "唐门", "地点/唐门", -323.6, 23.5),
    ("A_江陵", "江陵", "地点/江陵", 63.5, 52.7),
    ("B_锦香宫", "锦香宫", "地点/锦香宫", 50.0, -2.7),
    ("C_点苍", "点苍山", "地点/点苍山", -498.8, -238.7),
    ("D_青城", "青城山", "地点/青城山", -456.3, 83.6),
    ("E_雪山", "大雪山", "地点/大雪山", -431.3, 240.7),
    ("F_崆峒", "崆峒山", "地点/崆峒山", -315.4, 305.4),
    ("G_全真", "全真派", "势力/全真派", -125.8, 191.6),
    ("H_六道峡", "六道峡", "地点/六道峡", 34.9, 88.2),
    ("I_嵩山", "嵩山", "地点/嵩山", 9.2, 218.6),
    ("J_峨嵋", "峨嵋山", "地点/峨嵋山", -510.3, -61.7),
    ("K2_卧云岗", "卧云岗", "地点/卧云岗", -204.1, -101.0),
    ("L_襄阳", "襄阳", "地点/襄阳", 114.6, 89.9),
]
WAY = [(-291.6, -29.6), (-224.1, -5.1), (-155.6, 18.8), (-102.0, 40.1),
       (-54.4, 49.2), (-12.0, 54.5), (20.2, 64.0), (-364.7, 62.4),
       (-408.2, 74.9), (-318.8, 100.9), (-316.1, 145.1), (-346.7, 188.7),
       (-375.2, 206.2), (-333.0, 217.8), (-312.3, 241.2), (-294.0, 270.5),
       (-426.7, 214.6), (-429.2, -74.5), (-361.2, -86.0), (-314.7, -66.5),
       (-259.8, -91.4), (-177.1, -131.9), (-257.6, 260.6), (-217.3, 257.5),
       (70.9, 99.4)]

im = Image.open(SRC).convert("RGBA")
W, H = im.size
flat = Image.new("RGB", (W, H), (246, 241, 229))
flat.paste(im, (0, 0), im)
out_img = os.path.join(WEB, "map_bg.jpg")
flat.save(out_img, quality=88, optimize=True, progressive=True)
print("底图 %s  %dx%d  %.2f MB" % (out_img, W, H, os.path.getsize(out_img) / 1048576))


def to_px(x, y):
    return ((x + 960.0) / 1920.0 * W, (540.0 - y) / 1080.0 * H)


LAB_H = 96.0
FONT_W = 62.0


def rects_overlap(a, b, pad=10):
    return not (a[2] + pad < b[0] or b[2] + pad < a[0]
                or a[3] + pad < b[1] or b[3] + pad < a[1])


dots = []
for nm, label, slug, x, y in NAMED:
    px, py = to_px(x, y)
    dots.append((px, py, 26))
for x, y in WAY:
    px, py = to_px(x, y)
    dots.append((px, py, 16))

placed = []
nodes = []
for nm, label, slug, x, y in NAMED:
    px, py = to_px(x, y)
    tw = len(label) * FONT_W + 24
    cands = []
    for _dy in (0, -46, 46, -92, 92):
        cands.append(("right", (px + 34, py - LAB_H / 2 + _dy, px + 34 + tw, py + LAB_H / 2 + _dy)))
        cands.append(("left", (px - 34 - tw, py - LAB_H / 2 + _dy, px - 34, py + LAB_H / 2 + _dy)))
    for _dx in (0, -70, 70):
        cands.append(("up", (px - tw / 2 + _dx, py - 34 - LAB_H, px + tw / 2 + _dx, py - 34)))
        cands.append(("down", (px - tw / 2 + _dx, py + 34, px + tw / 2 + _dx, py + 34 + LAB_H)))
    pick = None
    for side, r in cands:
        if r[0] < 12 or r[1] < 12 or r[2] > W - 12 or r[3] > H - 12:
            continue
        bad = any(rects_overlap(r, q) for q in placed)
        if not bad:
            for dx, dy, dr in dots:
                if (r[0] - dr < dx < r[2] + dr) and (r[1] - dr < dy < r[3] + dr):
                    bad = True
                    break
        if not bad:
            pick = (side, r)
            break
    if not pick:
        pick = cands[0]
    placed.append(pick[1])
    nodes.append({"name": label, "slug": slug, "key": nm,
                  "x": round(px / W * 100, 3), "y": round(py / H * 100, 3),
                  "side": pick[0],
                  "dy": round((pick[1][1] + pick[1][3]) / 2 - py, 1)})

ways = [{"x": round(to_px(x, y)[0] / W * 100, 3),
         "y": round(to_px(x, y)[1] / H * 100, 3)} for x, y in WAY]

data = {"img": "/static/map_bg.jpg", "w": W, "h": H, "nodes": nodes, "ways": ways}
p = os.path.join(WEB, "map_nodes.json")
json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("节点", len(nodes), "途经", len(ways), "->", p)
for n in nodes:
    print("   %-6s %-10s %5.1f%% %5.1f%%  %s" % (n["name"], n["key"], n["x"], n["y"], n["side"]))
