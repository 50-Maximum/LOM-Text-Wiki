# -*- coding: utf-8 -*-
"""测量轻量化空间：DB 压缩/去 FTS 后体积、立绘尺寸。"""
import io, os, shutil, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
src = os.path.join(B, "data", "wiki.db")
tmp = os.path.join(B, "data", "_lite_probe.db")
print("原库 %.1f MB" % (os.path.getsize(src) / 1048576))

shutil.copyfile(src, tmp)
c = sqlite3.connect(tmp)
c.execute("vacuum")
c.close()
print("VACUUM 后 %.1f MB" % (os.path.getsize(tmp) / 1048576))

shutil.copyfile(src, tmp)
c = sqlite3.connect(tmp)
for t in ["lines_fts_data", "lines_fts_idx", "lines_fts_docsize", "lines_fts_config", "lines_fts"]:
    try:
        c.execute("drop table if exists %s" % t)
    except Exception as e:
        print("  drop", t, e)
c.commit()
c.execute("vacuum")
c.close()
print("去 FTS 后 %.1f MB" % (os.path.getsize(tmp) / 1048576))
os.remove(tmp)

from PIL import Image
d = os.path.join(B, "web", "portrait")
files = sorted(os.listdir(d))[:3]
tot = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d) if f.lower().endswith(".png"))
n = sum(1 for f in os.listdir(d) if f.lower().endswith(".png"))
print("立绘 %d 张，共 %.1f MB，均 %.2f MB" % (n, tot / 1048576, tot / max(1, n) / 1048576))
for f in files:
    p = os.path.join(d, f)
    im = Image.open(p)
    print("   %-28s %s %s %.2f MB" % (f, im.width, im.height, os.path.getsize(p) / 1048576))
