# -*- coding: utf-8 -*-
"""把 level2 大地图坐标画到 background_map 上，生成可核对的对位预览图。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat

ART = r"D:\LegendOfMortal Wiki\data\art_dump"
OUTDIR = r"D:\LegendOfMortal Wiki\data\art_dump"

MAP = os.path.join(ART, "Texture2D__background_map__sharedassets2_assets.png")
SAMPLE = os.path.join(ART, "Texture2D__background_map_sample__sharedassets2_assets.png")

# level2 / Map 命名点（canvas 1920x1080，中心为原点）
NAMED = [
    ("Home", "唐门", -323.6, 23.5),
    ("A_江陵", "江陵", 63.5, 52.7),
    ("B_锦香宫", "锦香宫", 50.0, -2.7),
    ("C_点苍", "点苍山", -498.8, -238.7),
    ("D_青城", "青城山", -456.3, 83.6),
    ("E_雪山", "大雪山", -431.3, 240.7),
    ("F_崆峒", "崆峒山", -315.4, 305.4),
    ("G_全真", "全真教", -125.8, 191.6),
    ("H_六道峡", "六道峡", 34.9, 88.2),
    ("I_嵩山", "嵩山", 9.2, 218.6),
    ("J_峨嵋", "峨嵋山", -510.3, -61.7),
    ("K2_卧云岗", "卧云岗", -204.1, -101.0),
    ("L_襄阳", "襄阳", 114.6, 89.9),
]
WAY = [("A1", -291.6, -29.6), ("A2", -224.1, -5.1), ("A3", -155.6, 18.8),
       ("A4", -102.0, 40.1), ("A5", -54.4, 49.2), ("A6", -12.0, 54.5),
       ("A7", 20.2, 64.0), ("D1", -364.7, 62.4), ("D2", -408.2, 74.9),
       ("F1", -318.8, 100.9), ("F2", -316.1, 145.1), ("F3", -346.7, 188.7),
       ("F4", -375.2, 206.2), ("F5", -333.0, 217.8), ("F6", -312.3, 241.2),
       ("F7", -294.0, 270.5), ("E1", -426.7, 214.6), ("J1", -429.2, -74.5),
       ("J2", -361.2, -86.0), ("J3", -314.7, -66.5), ("K1", -259.8, -91.4),
       ("K3", -177.1, -131.9), ("F7_1", -257.6, 260.6), ("F7_2", -217.3, 257.5),
       ("H1", 70.9, 99.4)]
PATHS = [("Home_A1", -321.3, 21.5), ("D1_D", -364.3, 61.8), ("Home_D1", -324.4, 22.7),
         ("D1_F1", -365.7, 61.4), ("F1_F2", -319.5, 100.6), ("F2_F4", -317.0, 143.7),
         ("F4_E", -375.0, 207.2), ("F4_F", -375.0, 207.2), ("A1_A", -293.0, -29.6),
         ("F1_A2", -319.5, 100.6), ("F3_A6", -328.1, 173.3), ("J_A1", -508.3, -62.0),
         ("J3_K", -314.9, -67.2), ("A7_B", 21.3, 65.1), ("F7", -294.6, 271.1),
         ("A7_L", 22.4, 63.9)]

# 先看 map 与 sample 的差异结构
if os.path.exists(SAMPLE):
    a = Image.open(MAP).convert("RGB")
    b = Image.open(SAMPLE).convert("RGB")
    diff = ImageChops.difference(a, b).convert("L")
    st = ImageStat.Stat(diff)
    px = diff.load()
    big = sum(1 for y in range(0, diff.height, 4) for x in range(0, diff.width, 4)
              if px[x, y] > 24)
    print("map vs sample: mean=%.2f max=%d  差异>24 的采样点=%d/%d"
          % (st.mean[0], st.extrema[0][1], big,
             (diff.width // 4) * (diff.height // 4)))

im = Image.open(MAP).convert("RGBA")
W, H = im.size
bg = Image.new("RGB", (W, H), (245, 240, 228))
bg.paste(im, (0, 0), im)

d = ImageDraw.Draw(bg)
F = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 54)
FS = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 26)


def to_px(x, y):
    return ((x + 960.0) / 1920.0 * W, (540.0 - y) / 1080.0 * H)


for nm, x, y in PATHS:
    px, py = to_px(x, y)
    d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(120, 90, 60))
for nm, x, y in WAY:
    px, py = to_px(x, y)
    d.ellipse([px - 7, py - 7, px + 7, py + 7], outline=(90, 60, 30), width=3)
for nm, label, x, y in NAMED:
    px, py = to_px(x, y)
    r = 16
    d.ellipse([px - r, py - r, px + r, py + r], fill=(180, 40, 30), outline=(255, 255, 255), width=4)
    tw = d.textlength(label, font=F)
    d.rectangle([px + 22, py - 34, px + 22 + tw + 16, py + 34], fill=(255, 255, 255, 235))
    d.text((px + 30, py - 30), label, font=F, fill=(20, 20, 20))

prev = bg.copy()
prev.thumbnail((1600, 1600))
p1 = os.path.join(OUTDIR, "preview_map_marked.jpg")
prev.save(p1, quality=90)
print("预览:", p1, prev.size)

# 裁一块唐门周边看清底图是否对得上
cx, cy = to_px(-323.6, 23.5)
box = (int(cx - 420), int(cy - 420), int(cx + 420), int(cy + 420))
crop = bg.crop(box)
crop = crop.resize((760, 760))
p2 = os.path.join(OUTDIR, "preview_map_home.jpg")
crop.save(p2, quality=92)
print("唐门周边:", p2)
